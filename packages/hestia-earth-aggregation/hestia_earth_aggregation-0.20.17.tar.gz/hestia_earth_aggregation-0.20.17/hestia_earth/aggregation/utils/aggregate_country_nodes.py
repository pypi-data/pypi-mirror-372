import os
from math import sqrt
from functools import reduce
from typing import TypedDict, Optional, Dict, List, Union, Tuple, Set
from hestia_earth.schema import TermTermType, CycleJSONLD, SiteJSONLD, TermJSONLD
from hestia_earth.utils.tools import list_sum, list_average, non_empty_list, flatten, is_number, is_boolean
from hestia_earth.utils.blank_node import ArrayTreatment, get_node_value, _retrieve_array_treatment

from hestia_earth.aggregation.log import logger, log_memory_usage
from . import (
    CYCLE_AGGREGATION_KEYS, SITE_AGGREGATION_KEYS,
    pick, weighted_average, _min, _max, _sd, sum_data, format_aggregated_list, format_evs
)
from .term import _format_irrigated, _format_organic
from .completeness import (
    combine_completeness_count, sum_completeness_count, is_complete, completeness_count, blank_node_completeness_key
)
from .group import _filter_blank_nodes
from .blank_node import map_blank_node, default_missing_value, _blank_node_type, blank_node_group_key
from .queries import download_nodes, download_site
from .cycle import is_organic, is_irrigated, aggregate_with_matrix, _should_include_cycle
from .site import create_site, format_site_results
from .emission import get_method_tier
from .property import aggregate_properties
from .distribution import generate_blank_node_distribution
from .covariance import add_covariance_cycles, generate_covariance_cycles

_BATCH_SIZE = int(os.getenv('AGGREGATION_CYCLES_BATCH_SIZE', '1000'))


def _default_as_value(value: dict): return value.get('value')


def _default_sd(value: dict, array_treatment: ArrayTreatment):
    min_value = get_node_value(value, key='min', array_treatment=array_treatment, default=None)
    max_value = get_node_value(value, key='max', array_treatment=array_treatment, default=None)
    return [(max_value-min_value)/4] if all([min_value, max_value]) else None


def _map_sd(values: list, array_treatment: ArrayTreatment):
    def get_value(blank_node: dict):
        value = blank_node.get('sd') or _default_sd(blank_node, array_treatment)
        value = value if isinstance(value, list) else non_empty_list([value])
        return None if not value else sqrt(sum([
            v**2 for v in value
        ])) if array_treatment == ArrayTreatment.SUM else sqrt(sum([
            v**2 for v in value
        ])) / len(value)

    return flatten(non_empty_list(map(get_value, values)))


def _map_node_values(values: list, array_treatment: ArrayTreatment, key: str = 'value', fallback=lambda *args: None):
    def get_value(blank_node: dict):
        value = get_node_value(blank_node, key=key, array_treatment=array_treatment, default=None)
        return fallback(blank_node) if value is None else value

    return flatten(non_empty_list(map(get_value, values)))


def _map_values(values: list, key: str = 'value', include_empty: bool = False):
    results = flatten([v.get(key) for v in values])
    return results if include_empty else non_empty_list(results)


class BlankNodeFormatted(TypedDict, total=False):
    term: dict
    value: Optional[List[Union[str, int, float, bool]]]
    economicValueShare: Optional[List[Union[int, float]]]
    min: Optional[List[Union[int, float]]]
    max: Optional[List[Union[int, float]]]
    observations: Optional[int]
    complete: Optional[bool]
    completeness_key: Optional[str]
    start_date: Optional[str]
    end_date: str


# --- Cycle


class CycleFormatted(TypedDict, total=False):
    cycle_ids: List[str]
    site_ids: List[str]
    source_ids: List[str]
    site_durations: List[float]
    site_unused_durations: List[float]
    site_areas: List[float]
    completeness: Dict[str, int]
    product: TermJSONLD
    functionalUnit: str
    organic: bool
    irrigated: bool
    numberOfCycles: int
    inputs: Dict[str, BlankNodeFormatted]
    products: Dict[str, BlankNodeFormatted]
    practices: Dict[str, BlankNodeFormatted]
    emissions: Dict[str, BlankNodeFormatted]


def _cycle_product_value(cycle: dict, product: dict):
    return list_sum(flatten([
        # account for every product with the same `@id`
        p.get('value', []) for p in cycle.get('products', [])
        if p.get('term', {}).get('@id') == product.get('@id')
    ]), default=None)


def _blank_node_evs(blank_nodes: List[BlankNodeFormatted]) -> Union[None, int, float]:
    values = _map_values(blank_nodes, 'economicValueShare')
    return None if not values else list_sum(values)


def _combine_blank_nodes_stats(blank_nodes: List[BlankNodeFormatted]):
    """
    Combine multiple blank nodes with the same term, into a single list of stats.
    """
    array_treatment = _retrieve_array_treatment(blank_nodes[0], default=ArrayTreatment.SUM)
    return {
        'value': _map_node_values(blank_nodes, array_treatment),
        'min': _map_node_values(blank_nodes, array_treatment, 'min', fallback=_default_as_value),
        'max': _map_node_values(blank_nodes, array_treatment, 'max', fallback=_default_as_value),
        'sd': _map_sd(blank_nodes, array_treatment)
    }


def _group_cycle_blank_node(cycle: dict, product: dict, product_value: float):
    """
    Group all blanks nodes within a single Cycle, using the term `@id` and some other keys.
    This will group with any other existing blank node in the same group, and keep only one value.
    """
    def grouper(group: dict, blank_node: dict) -> Dict[str, BlankNodeFormatted]:
        term = blank_node.get('term', {})
        node_type = _blank_node_type(blank_node)
        term_id = term.get('@id')
        group_key = blank_node_group_key(blank_node)

        is_aggregated_product = node_type == 'Product' and term_id == product.get('@id')

        complete = is_complete(cycle, product, blank_node)

        blank_node_data: BlankNodeFormatted = map_blank_node(
            blank_node | {
                'complete': complete,
                'completeness_key': blank_node_completeness_key(blank_node, product)
            },
            is_aggregated_product=is_aggregated_product
        )

        # only primary data can be incomplete, otherwise skip the blank node
        if all([
            complete is False,
            not blank_node_data.get('primary'),
            blank_node_data.get('primaryPercent', 0) <= 0,
        ]):
            return group

        normalize_value = product.get('termType') != TermTermType.CROP.value
        value = blank_node_data['value']
        blank_node_data['value'] = (
            value / (product_value if product_value else 1)
        ) if normalize_value and is_number(value) else value

        # if there is an existing blank node in the same group, combine to get a single value
        existing_data: BlankNodeFormatted = group.get(group_key)

        blank_nodes = non_empty_list([existing_data, blank_node_data])
        data = (existing_data or {}) | blank_node_data | _combine_blank_nodes_stats(blank_nodes) | {
            'economicValueShare': non_empty_list([_blank_node_evs(blank_nodes)]),
            # needed for background emissions
            'inputs': _map_values(blank_nodes, 'inputs'),
            'properties': _map_values(blank_nodes, 'properties'),
            'methodTier': get_method_tier(blank_nodes),
            'primary': any([n.get('primary') for n in blank_nodes]),
            'primaryPercent': _map_values(blank_nodes, 'primaryPercent')
        }
        group[group_key] = data
        return group
    return grouper


def _compute_blank_node_stats(blank_node: BlankNodeFormatted):
    """
    Combine a single blank nodes with multiple stats, into a single list of stats.
    """
    array_treatment = _retrieve_array_treatment(blank_node, default=ArrayTreatment.SUM)
    value = get_node_value(blank_node, array_treatment=array_treatment, default=None)
    min = (
        _min(blank_node.get('min', []), min_observations=1) if array_treatment == ArrayTreatment.MEAN else
        get_node_value(blank_node, key='min', array_treatment=array_treatment, default=None)
    )
    max = (
        _max(blank_node.get('max', []), min_observations=1) if array_treatment == ArrayTreatment.MEAN else
        get_node_value(blank_node, key='max', array_treatment=array_treatment, default=None)
    )
    sd_values = flatten([v for v in blank_node.get('sd', [])])
    sd = sqrt(sum([v**2 for v in sd_values])) if sd_values else None
    sd = (
        sd / len(sd_values) if array_treatment == ArrayTreatment.MEAN else sd
    ) if sd else None
    return {
        'value': value,
        'min': min,
        'max': max,
        'sd': sd,
        'observations': 0 if value is None else 1
    }


def _group_cycle_blank_nodes(
    cycle: dict,
    product: dict,
    product_value: float,
    start_year: int = None,
    end_year: int = None
):
    def grouper(group: dict, list_key: str) -> Dict[str, Dict[str, BlankNodeFormatted]]:
        blank_nodes = _filter_blank_nodes(cycle, list_key, start_year, end_year)
        values = reduce(_group_cycle_blank_node(cycle, product, product_value), blank_nodes, {})
        # after combining all values, need to compute the final statistical values
        group[list_key] = {
            k: v | _compute_blank_node_stats(v)
            for k, v in values.items()
        }
        return group
    return grouper


def _format_cycle(
    cycle: CycleJSONLD,
    product: TermJSONLD,
    start_year: int = None,
    end_year: int = None
) -> Tuple[List[CycleFormatted], Set[str]]:
    """
    Format Cycles to be used in grouping.
    Returns the list of formatted Cycles, and the list of Site ids to be downloaded.
    Note: if a Site does not have an `@id`, it means it's nested within the Cycle.
    """
    product_value = _cycle_product_value(cycle, product)
    data: CycleFormatted = (
        pick(cycle, ['functionalUnit', 'endDate']) | {
            'cycle_ids': [cycle.get('@id')],
            'site_ids': [cycle.get('site', {}).get('@id')],
            'source_ids': [cycle.get('defaultSource', {}).get('@id')],
            'site_durations': non_empty_list([cycle.get('siteDuration')]),
            'site_unused_durations': non_empty_list([cycle.get('siteUnusedDuration')]),
            'site_areas': non_empty_list([cycle.get('siteArea')]),
            'completeness': combine_completeness_count([cycle.get('completeness')]),
            'product': product,
            'organic': is_organic(cycle),
            'irrigated': is_irrigated(cycle),
            'numberOfCycles': cycle.get('numberOfCycles') or 1
        } |
        reduce(
            _group_cycle_blank_nodes(cycle, product, product_value, start_year, end_year),
            CYCLE_AGGREGATION_KEYS,
            {}
        )
    ) if _should_include_cycle(cycle) else None
    if data:
        logger.debug(
            'id=%s, yield=%s, organic=%s, irrigated=%s',
            cycle.get('@id'),
            product_value,
            data['organic'],
            data['irrigated']
        )
    return data if product_value is not None else None


def _combine_cycle_blank_node(
    cycles: List[CycleFormatted],
    list_key: str,
    completeness: Dict[str, int],
    cycle_count: int
):
    """
    Group blank nodes among multiple Cycles, to keep only one data entry with all the values.
    """
    def grouper(group: dict, group_key: str):
        values: List[BlankNodeFormatted] = non_empty_list([cycle.get(list_key, {}).get(group_key) for cycle in cycles])
        value = _map_values(values, include_empty=True)
        term = values[0].get('term')
        complete_key = values[0].get('completeness_key')
        complete_count = completeness_count(completeness, complete_key)
        default_value = default_missing_value(term)
        missing_values = ([default_value] * (complete_count - len(value)))
        primary_percent = _map_values(values, 'primaryPercent')
        data: BlankNodeFormatted = {
            **values[0],
            'value': value + missing_values,
            'economicValueShare': _map_values(values, 'economicValueShare'),
            'min': _map_values(values, 'min', include_empty=True),
            'max': _map_values(values, 'max', include_empty=True),
            'sd': _map_values(values, 'sd', include_empty=True),
            'observations': len(value + missing_values),
            'inputs': list({v.get('@id'): v for v in _map_values(values, 'inputs')}.values()),
            'properties': _map_values(values, 'properties'),
            'methodTier': get_method_tier(values),
            'primaryPercent': primary_percent + ([0] * (cycle_count - len(primary_percent)))
        }
        group[group_key] = data
        return group
    return grouper


def _combine_cycle_blank_nodes(cycles: List[CycleFormatted], completeness: Dict[str, int], cycle_count: int):
    def combine(group: dict, list_key: str):
        # get all possible keys first, then group each key values into a single blank node
        keys = set(flatten([list(cycle.get(list_key, {}).keys()) for cycle in cycles]))
        group[list_key] = reduce(_combine_cycle_blank_node(cycles, list_key, completeness, cycle_count), keys, {})
        return group
    return combine


def _combine_cycle_lists(cycles: List[CycleFormatted]):
    def combine(group: dict, key: str):
        group[key] = flatten([v.get(key, []) for v in cycles])
        return group
    return combine


def _combine_formatted_cycles(cycles: List[CycleFormatted]) -> CycleFormatted:
    completeness = sum_completeness_count([v['completeness'] for v in cycles])
    cycle_ids = flatten([v['cycle_ids'] for v in cycles])
    cycle_count = len(cycle_ids)
    data: CycleFormatted = pick(cycles[0], ['product', 'functionalUnit', 'organic', 'irrigated']) | {
        'cycle_ids': cycle_ids,
        'completeness': completeness,
        'numberOfCycles': sum_data(cycles, 'numberOfCycles')
    } | reduce(
        _combine_cycle_blank_nodes(cycles, completeness, cycle_count), CYCLE_AGGREGATION_KEYS, {}
    ) | reduce(
        _combine_cycle_lists(cycles), [
            'site_ids', 'source_ids', 'endDate', 'site_durations', 'site_unused_durations', 'site_areas'
        ], {}
    )
    return data


# --- Site


class SiteFormatted(TypedDict, total=False):
    site_ids: List[str]
    source_ids: List[str]
    numberOfSites: int
    measurements: Dict[str, BlankNodeFormatted]
    management: Dict[str, BlankNodeFormatted]


def _group_site_blank_node():
    def grouper(group: dict, blank_node: dict) -> Dict[str, BlankNodeFormatted]:
        """
        Group a single blank node, using the term `@id` and optionally some other keys.
        This will group with any other existing blank node in the same group, and keep only one value.
        """
        group_key = blank_node_group_key(blank_node)

        blank_node_data: BlankNodeFormatted = map_blank_node(blank_node)

        # if there is an existing blank node in the same group, combine to get a single value
        existing_data: BlankNodeFormatted = group.get(group_key)

        blank_nodes = non_empty_list([existing_data, blank_node_data])
        values = _map_values(blank_nodes)
        value = any(values) if all(map(is_boolean, values)) else get_node_value({'value': values})
        min = _min(_map_values(blank_nodes, 'min') + [value], min_observations=1)
        max = _max(_map_values(blank_nodes, 'max') + [value], min_observations=1)
        data = (existing_data or {}) | blank_node_data | {
            'value': value,
            'min': min,
            'max': max,
            'properties': _map_values(blank_nodes, 'properties')
        }
        group[group_key] = data
        return group
    return grouper


def _group_site_blank_nodes(site: SiteJSONLD, start_year: int = None, end_year: int = None):
    def grouper(group: dict, list_key: str) -> Dict[str, BlankNodeFormatted]:
        blank_nodes = _filter_blank_nodes(site, list_key, start_year, end_year)
        group[list_key] = reduce(_group_site_blank_node(), blank_nodes, {})
        return group
    return grouper


def _format_site(site: SiteJSONLD, start_year: int = None, end_year: int = None) -> SiteFormatted:
    data: SiteFormatted = pick(site, ['country', 'siteType']) | {
        'site_ids': [site.get('@id') or site.get('id')],
        'source_ids': [site.get('defaultSource', {}).get('@id')],
        'numberOfSites': site.get('numberOfSites') or 1
    } | reduce(
        _group_site_blank_nodes(site, start_year, end_year),
        SITE_AGGREGATION_KEYS,
        {}
    )
    return data


def _combine_site_blank_node(sites: List[SiteFormatted], list_key: str):
    def grouper(group: dict, group_key: str):
        values: List[BlankNodeFormatted] = non_empty_list([site.get(list_key, {}).get(group_key) for site in sites])
        value = _map_values(values, include_empty=True)
        data: BlankNodeFormatted = {
            **values[0],
            'value': value,
            'min': _map_values(values, 'min', include_empty=True),
            'max': _map_values(values, 'max', include_empty=True),
            'observations': len(non_empty_list(value)),
            'properties': _map_values(values, 'properties')
        }
        group[group_key] = data
        return group
    return grouper


def _combine_site_blank_nodes(sites: List[SiteFormatted]):
    def combine(group: dict, list_key: str):
        # get all possible keys first, then group each key values into a single blank node
        keys = set(flatten([list(site.get(list_key, {}).keys()) for site in sites]))
        group[list_key] = reduce(_combine_site_blank_node(sites, list_key), keys, {})
        return group
    return combine


def _combine_formatted_sites(sites: List[SiteFormatted]) -> SiteFormatted:
    data: SiteFormatted = pick(sites[0], ['country', 'siteType']) | {
        'site_ids': flatten([v['site_ids'] for v in sites]),
        'source_ids': flatten([v['source_ids'] for v in sites]),
        'numberOfSites': sum_data(sites, 'numberOfSites')
    } | reduce(_combine_site_blank_nodes(sites), SITE_AGGREGATION_KEYS, {})
    return data


# --- Aggregate


def _aggregate_blank_node(blank_node: BlankNodeFormatted):
    values = non_empty_list(blank_node.get('value', []))
    value = weighted_average([(v, 1) for v in values]) if values else None
    economicValueShare = weighted_average([(v, 1) for v in non_empty_list(blank_node.get('economicValueShare') or [])])

    distribution = generate_blank_node_distribution(blank_node)

    return pick(blank_node | {
        'value': value,
        'economicValueShare': format_evs(economicValueShare),
        'min': _min(non_empty_list(blank_node.get('min', []))),
        'max': _max(non_empty_list(blank_node.get('max', []))),
        'sd': _sd(non_empty_list(blank_node.get('value', []))),
        'properties': aggregate_properties(blank_node.get('properties', [])),
        'primaryPercent': list_average(non_empty_list(blank_node.get('primaryPercent', [])), default=None),
        'distribution': distribution
    }, [
        'term',
        'observations', 'inputs', 'methodTier', 'depthUpper', 'depthLower', 'startDate', 'endDate',
        'value', 'economicValueShare', 'min', 'max', 'sd', 'primary', 'primaryPercent', 'properties',
        'distribution'
    ])


def _aggregate_formatted(data: Union[CycleFormatted, SiteFormatted], aggregated_keys: List[str]):
    return reduce(
        lambda group, key: group | {key: list(map(_aggregate_blank_node, data.get(key, {}).values()))},
        aggregated_keys,
        {}
    )


def _group_cycles(cycles: list) -> dict[str, list]:
    """
    Group cycles by organic/irrigated.
    """
    def group_by(data: dict, cycle: dict):
        group_key = '-'.join([
            _format_organic(cycle.get('organic', False)),
            _format_irrigated(cycle.get('irrigated', False))
        ])
        data[group_key] = data.get(group_key, []) + [cycle]
        return data
    return reduce(group_by, cycles, {})


def _combine_cycles_batch(cycles: list, product: dict, start_year: int, end_year: int) -> Dict[str, CycleFormatted]:
    cycles = download_nodes(cycles)
    if not cycles:
        logger.warning('No cycles found, stopping aggregations.')
        return {}

    cycles = non_empty_list([_format_cycle(cycle, product, start_year, end_year) for cycle in cycles])

    include_matrix = aggregate_with_matrix(product)
    cycles = _group_cycles(cycles) if include_matrix else {'all': cycles}

    # add data to generate covariance
    [add_covariance_cycles(cycles=value, suffix=key) for key, value in cycles.items()]

    cycles = {
        key: _combine_formatted_cycles(value) for key, value in cycles.items()
    }

    if len(cycles.keys()) == 0:
        logger.debug('No cycles to run aggregation.')
        return {}

    return cycles


def _combine_sites_batch(
    site_ids: List[str],
    start_year: int,
    end_year: int
) -> Dict[str, SiteFormatted]:
    # the same site can be used multiple times
    sites_by_id = {
        site_id: _format_site(download_site({'@type': 'Site', '@id': site_id}), start_year, end_year)
        for site_id in set(site_ids)
    }
    return _combine_formatted_sites([sites_by_id[site_id] for site_id in site_ids])


def _aggregate_sites(site_ids: List[str], start_year: int, end_year: int) -> SiteJSONLD:
    batches = range(0, len(site_ids), _BATCH_SIZE)

    all_sites = []

    for batch_index in batches:
        logger.info(f"Processing sites in batch {int(batch_index / _BATCH_SIZE) + 1} of {len(batches)}...")
        log_memory_usage()
        batched_site_ids = site_ids[batch_index:batch_index + _BATCH_SIZE]
        site = _combine_sites_batch(batched_site_ids, start_year, end_year)
        all_sites.append(site)

    logger.info('Finished processing batch, combining all sites...')
    log_memory_usage()

    site = _combine_formatted_sites(all_sites)
    site = (
        create_site(pick(site, ['country', 'siteType'])) |
        format_site_results(_aggregate_formatted(site, SITE_AGGREGATION_KEYS)) | {
            'aggregatedSites': format_aggregated_list('Site', site['site_ids']),
            'aggregatedSources': format_aggregated_list('Source', site['source_ids']),
            'numberOfSites': site.get('numberOfSites')
        }
    )
    return site


def aggregate_cycles(cycles: list, product: dict, start_year: int, end_year: int):
    batches = range(0, len(cycles), _BATCH_SIZE)
    logger.info(f"Processing {len(cycles)} cycles in {len(batches)} batches.")

    all_cycles: Dict[str, List[CycleFormatted]] = {}

    # step 1: combine and aggregate all cycles by group
    for batch_index in batches:
        logger.info(f"Processing cycles in batch {int(batch_index / _BATCH_SIZE) + 1} of {len(batches)}...")
        log_memory_usage()
        batched_cycles = cycles[batch_index:batch_index + _BATCH_SIZE]
        batch_cycles = _combine_cycles_batch(batched_cycles, product, start_year, end_year)
        for key, value in batch_cycles.items():
            all_cycles[key] = all_cycles.get(key, []) + [value]

    logger.info('Finished processing batch, combining all cycles...')
    log_memory_usage()
    # generate covariance on sub cycles
    covariances = {
        key: generate_covariance_cycles(key)
        for key in all_cycles.keys()
    }
    all_cycles = {
        key: _combine_formatted_cycles(cycles=values)
        for key, values in all_cycles.items()
    }
    # add covariances to cycles once they have been combined
    cycles = [
        cycle | covariances[key]
        for key, cycle in all_cycles.items()
    ]
    # discard memory
    all_cycles = {}

    # step 2: combine and aggregate all sites by group
    logger.info('Finished combining cycles, processing sites...')
    log_memory_usage()
    sites = [
        _aggregate_sites(value.get('site_ids', []), start_year, end_year)
        for value in cycles
    ]

    logger.info('Finished aggregating sites, aggregating cycles...')
    log_memory_usage()
    cycles: List[CycleFormatted] = [
        (
            cycle |
            {'site': sites[index]} |
            _aggregate_formatted(cycle, CYCLE_AGGREGATION_KEYS)
        )
        for index, cycle in enumerate(cycles)
    ]
    cycles = [
        # map fields for `format_term_results`
        cycle | {
            'node-ids': cycle['cycle_ids'],
            'source-ids': cycle['source_ids'],
            'completeness-count': cycle['completeness']
        }
        for cycle in cycles
    ]
    log_memory_usage()
    return cycles
