from typing import List
from functools import reduce
from hestia_earth.schema import SchemaType
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, find_term_ids_by
from hestia_earth.utils.tools import non_empty_list, flatten, list_sum, is_number, safe_parse_float
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.blank_node import get_node_value

from hestia_earth.aggregation.log import logger
from . import pick, match_dates
from .term import DRY_MATTER_TERM_ID, term_dryMatter, should_aggregate
from .completeness import emission_completeness_key
from .management import aggregated_dates

_GROUP_KEYS_100 = [
    'sumMax100Group',
    'sumIs100Group'
]


def _blank_node_type(blank_node: dict): return blank_node.get('@type') or blank_node.get('type')


def get_lookup_value(lookup_term: dict, column: str):
    table_name = f"{lookup_term.get('termType')}.csv" if lookup_term else None
    return get_table_value(
        download_lookup(table_name), 'termid', lookup_term.get('@id'), column_name(column)
    ) if table_name else None


def _formatDepth(depth: str):
    # handle float values
    return str(int(depth)) if is_number(depth) else ''


def default_missing_value(term: dict):
    # value can be string, number or boolean
    # use lookup `valueType` to determine which value to add
    value_type = get_lookup_value(term, 'valueType')
    return {'boolean': False}.get(value_type, 0)


def _node_dryMatter(blank_node: dict):
    return safe_parse_float(find_term_match(blank_node.get('properties', []), DRY_MATTER_TERM_ID).get('value'))


def node_dryMatter_rescale_ratio(blank_node: dict):
    """
    Return the rescale ratio between the user provided `dryMatter` and HESTIA default `dryMatter`.
    """
    # for products with the `dryMatter` property, need to rescale using our default value
    node_dm = _node_dryMatter(blank_node)
    default_dm = term_dryMatter(blank_node.get('term', {})) if node_dm else 0
    return node_dm / default_dm if all([node_dm, default_dm]) else 1


def _blank_node_dates(blank_node: dict):
    node_type = _blank_node_type(blank_node)
    return aggregated_dates(blank_node) if node_type == SchemaType.MANAGEMENT.value else (
        pick(blank_node, ['startDate', 'endDate'])
    )


def _properties_group(blank_node: dict):
    properties = [p for p in blank_node.get('properties', []) if should_aggregate(p.get('term', {}))]
    group_key = '-'.join(non_empty_list([
        get_lookup_value(prop.get('term'), 'blankNodesGroup') or prop.get('term', {}).get('@id')
        for prop in properties
    ]))
    return group_key


def _default_blank_node_group_key(blank_node: dict, include_dates: bool = True):
    node_type = _blank_node_type(blank_node)
    keys = non_empty_list([
        _formatDepth(blank_node.get('depthUpper')),
        _formatDepth(blank_node.get('depthLower')),
        blank_node.get('startDate') if include_dates else '',
        blank_node.get('endDate') if include_dates else '',
        emission_completeness_key(blank_node) if node_type == SchemaType.EMISSION.value else '',
        _properties_group(blank_node)
    ])
    return '-'.join(keys)


def blank_node_group_key(blank_node: dict):
    keys = non_empty_list([
        _default_blank_node_group_key(blank_node, include_dates=_blank_node_type(blank_node) in [
            SchemaType.MANAGEMENT.value,
            SchemaType.MEASUREMENT.value,
        ]),
        blank_node.get('term', {}).get('@id')
    ])
    return '-'.join(keys)


def group_by_term_id(group: dict, node: dict):
    group_key = blank_node_group_key(node)
    group[group_key] = group.get(group_key, []) + [node]
    return group


def _group_blank_nodes(nodes: list):
    """
    Group a list of blank nodes using:
    - `termType`
    - the `depthUpper` and `depthLower`
    - the `startDate` and `endDate`
    - the lookup group `sumMax100Group` or `sumIs100Group` or `booleanGroup` if specified

    Parameters
    ----------
    nodes : list
        List of blank nodes with their index.
    """
    def group_by(group: dict, blank_node: dict):
        term = blank_node.get('term', {})
        term_type = term.get('termType')
        lookup = download_lookup(f"{term_type}.csv")
        sum_below_100_group = get_table_value(lookup, 'termid', term.get('@id'), column_name('sumMax100Group')) \
            if lookup is not None else None
        sum_equal_100_group = get_table_value(lookup, 'termid', term.get('@id'), column_name('sumIs100Group')) \
            if lookup is not None else None
        boolean_group = get_table_value(lookup, 'termid', term.get('@id'), column_name('booleanGroup')) \
            if lookup is not None else None

        keys = non_empty_list([
            _default_blank_node_group_key(blank_node),
            term_type,
            sum_below_100_group,
            sum_equal_100_group,
            boolean_group
        ])
        key = '-'.join(keys)

        group[key] = group.get(key, []) + [{
            'key': key,
            'node': blank_node,
            'sumMax100Group': sum_below_100_group,
            'sumIs100Group': sum_equal_100_group,
            'booleanGroup': boolean_group
        }]

        return group

    return reduce(group_by, nodes, {})


def _filter_by_array_treatment(blank_node: dict):
    term = blank_node.get('term', {})
    lookup = download_lookup(f"{term.get('termType')}.csv")
    value = get_table_value(lookup, 'termid', term.get('@id'), column_name('arrayTreatmentLargerUnitOfTime'))
    # ignore any blank node with time-split data
    return not value


def _filter_needs_depth(blank_node: dict):
    term = blank_node.get('term', {})
    lookup = download_lookup(f"{term.get('termType')}.csv")
    needs_depth = get_table_value(lookup, 'termid', term.get('@id'), column_name('recommendAddingDepth'))
    return not needs_depth or all([blank_node.get('depthUpper') is not None, blank_node.get('depthLower') is not None])


def _missing_blank_node(node_type: str, term_type: str, term_id: str, units: str):
    term = {'@type': 'Term', 'termType': term_type, '@id': term_id, 'units': units}
    return {
        '@type': node_type,
        'term': term,
        'value': [default_missing_value(term)]
    }


def _add_missing_blank_nodes(blank_nodes: List[dict], lookup_group_key: str):
    existing_ids = [v.get('node').get('term', {}).get('@id') for v in blank_nodes]
    group_id = blank_nodes[0].get(lookup_group_key)
    blank_node = blank_nodes[0].get('node')
    node_type = _blank_node_type(blank_node)
    term = blank_node.get('term', {})
    term_type = term.get('termType')
    units = term.get('units')
    lookup = download_lookup(f"{term_type}.csv")
    term_ids = find_term_ids_by(lookup, column_name(lookup_group_key), group_id)
    missing_term_ids = [term_id for term_id in term_ids if term_id not in existing_ids]
    return [
        _missing_blank_node(node_type, term_type, term_id, units) | pick(blank_node, [
            'startDate', 'endDate', 'properties'
        ])
        for term_id in missing_term_ids
    ]


def _filter_grouped_nodes(blank_nodes: List[dict]):
    values = flatten([v.get('node').get('value', []) for v in blank_nodes])
    total_value = list_sum(values)
    is_100_total = 99.5 <= total_value <= 100.5
    blank_node = blank_nodes[0]

    group_key_100 = next((k for k in _GROUP_KEYS_100 if blank_node.get(k)), None)
    # only use 100 group if the total is 100% as otherwise we can not validate to 100%
    is_group_key_100_valid = all([group_key_100, is_100_total])
    additional_blank_nodes = _add_missing_blank_nodes(blank_nodes, group_key_100) if is_group_key_100_valid else []
    if all([group_key_100, not is_100_total, total_value > 0]):
        logger.debug('Sum of group %s equal to %s, skipping.', blank_node.get('key'), total_value)

    dates = _blank_node_dates(blank_node.get('node'))
    return [
        r | dates
        for r in (
            [v.get('node') for v in blank_nodes] + additional_blank_nodes
        )
    ] if not group_key_100 or is_group_key_100_valid else []


def node_type_allowed(term: dict, node_type: str):
    lookup = download_lookup(f"{term.get('termType')}.csv")
    values = get_table_value(lookup, 'termid', term.get('@id'), column_name('skipAggregatedNodeTypes'))
    skipped_values = values.split(';') if values and isinstance(values, str) else []
    return 'all' not in skipped_values and node_type not in skipped_values


def filter_aggregate(blank_node: dict):
    term = blank_node.get('term', {})
    node_type = _blank_node_type(blank_node)
    return all([
        should_aggregate(term),
        node_type_allowed(term, node_type)
    ])


def filter_blank_nodes(blank_nodes: List[dict], start_year: int = None, end_year: int = None):
    nodes = [v for v in blank_nodes if all([
        filter_aggregate(v),
        _filter_by_array_treatment(v),
        # _filter_needs_depth(v),  # allow measurements without depths to be aggregated together
        not start_year or not end_year or match_dates(v, start_year, end_year),
        # ignore `Management` node with grouped `properties` as creating conflicts over same `tern`
        _blank_node_type(v) != SchemaType.MANAGEMENT.value or not _properties_group(v)
    ])]

    grouped_values = _group_blank_nodes(nodes)
    return flatten(map(_filter_grouped_nodes, grouped_values.values()))


def _is_value_zero(value):
    return value == [0] if isinstance(value, list) else (value == 0 or value == 0.0) if value is not None else False


def _remove_value_zero(blank_node: dict):
    term = blank_node.get('term', {})
    units = term.get('units')
    value = blank_node.get('value')
    return all([
        units == '% area',
        _is_value_zero(value)
    ]) and any([bool(get_lookup_value(term, key)) for key in _GROUP_KEYS_100])


def cleanup_blank_nodes(blank_nodes: List[dict]):
    # remove all blank nodes with `0` as value to reduce the node count
    return list(filter(lambda v: not _remove_value_zero(v), non_empty_list(blank_nodes)))


def _rescale_product_value_dm(node: dict, value: float):
    # for products with the `dryMatter` property, need to rescale using our default value
    rescale_ratio = node_dryMatter_rescale_ratio(node)
    return value * rescale_ratio


def _blank_node_value(blank_node: dict, complete: bool, is_aggregated_product: bool):
    """
    Handle completeness for `value` field.
    Rules:
    - if the blank_node is complete, use the value or set `0` if no value
    - if the blank_node is incomplete:
      - if it is the aggregated product, use the value
      - otherwise, do not use the value
    """
    default_value = default_missing_value(blank_node.get('term')) if complete else None
    value = get_node_value(blank_node, 'value', default=default_value)
    is_product = _blank_node_type(blank_node) == SchemaType.PRODUCT.value

    return (
        _rescale_product_value_dm(blank_node, value) if all([
            is_product,
            value
        ]) else value
    ) if complete is not False else (
        value if is_aggregated_product else None
    )


def _blank_node_evs(blank_node: dict, complete: bool, is_aggregated_product: bool):
    """
    Handle product evs.
    Only use the evs if the primary product is complete or has a value.
    """
    return blank_node.get('economicValueShare') if all([
        is_aggregated_product,
        complete or get_node_value(blank_node, 'value', default=0) != 0
    ]) else None


def _blank_node_sd(blank_node: dict):
    sd = blank_node.get('sd', [])
    return sum([v**2 for v in sd]) if sd else None


def map_blank_node(blank_node: dict, is_aggregated_product: bool = False):
    """
    Simplify blank node data by only keeping what we use in aggregation.
    """
    complete = blank_node.get('complete')
    value = _blank_node_value(blank_node, complete, is_aggregated_product)
    is_primary = blank_node.get('primary', False) or is_aggregated_product
    return blank_node | {
        'primary': is_primary,
        'value': value,
        'economicValueShare': _blank_node_evs(blank_node, complete, is_aggregated_product),
        'min': get_node_value(blank_node, 'min', default=None),
        'max': get_node_value(blank_node, 'max', default=None),
        'sd': _blank_node_sd(blank_node),
        'observations': 0 if value is None else 1,
        'properties': [
            pick(p, ['term', 'value'])
            for p in blank_node.get('properties', [])
            if should_aggregate(p.get('term', {}))
        ]
    }
