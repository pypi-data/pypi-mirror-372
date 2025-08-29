from hestia_earth.utils.tools import non_empty_list

from hestia_earth.aggregation.log import logger, log_memory_usage
from hestia_earth.aggregation.utils import CYCLE_AGGREGATION_KEYS, SITE_AGGREGATION_KEYS
from hestia_earth.aggregation.utils.queries import find_global_nodes, find_country_nodes, download_site
from hestia_earth.aggregation.utils.term import _is_global
from hestia_earth.aggregation.utils.quality_score import calculate_score, filter_min_score
from hestia_earth.aggregation.utils.group import group_blank_nodes
from hestia_earth.aggregation.utils.aggregate_weighted import aggregate as aggregate_weighted
from hestia_earth.aggregation.utils.aggregate_country_nodes import aggregate_cycles
from hestia_earth.aggregation.utils.weights import (
    country_weights, country_weight_node_id, world_weights, world_weight_node_id
)
from hestia_earth.aggregation.utils.site import format_site
from hestia_earth.aggregation.utils.cycle import (
    aggregate_with_matrix, format_for_grouping, format_terms_results, format_country_results, update_cycle
)
from hestia_earth.aggregation.utils.covariance import (
    init_covariance_files,
    remove_covariance_files,
    generate_covariance_country
)


def _aggregate_country(
    country: dict,
    product: dict,
    cycles: list,
    source: dict,
    start_year: int,
    end_year: int,
    multiple_countries: bool = False,
    generate_weights_func=None,
    missing_weights_node_id_func=None
) -> list:
    functional_unit = cycles[0].get('functionalUnit')

    # aggregate cycles with weights
    cycles_formatted = format_for_grouping(cycles)
    cycle_data = group_blank_nodes(cycles_formatted, CYCLE_AGGREGATION_KEYS, start_year, end_year, product=product)
    weights = generate_weights_func(cycle_data)
    cycle_data = cycle_data | aggregate_weighted(
        aggregate_keys=CYCLE_AGGREGATION_KEYS,
        data=cycle_data,
        weights=weights,
        missing_weights_node_id_func=missing_weights_node_id_func
    )

    # aggregate sites with weights
    sites = [c.get('site') for c in cycles]
    site_data = group_blank_nodes(sites, SITE_AGGREGATION_KEYS)
    site_data = aggregate_weighted(
        aggregate_keys=SITE_AGGREGATION_KEYS,
        data=site_data,
        weights=weights,
        missing_weights_node_id_func=missing_weights_node_id_func
    )
    aggregated_site = format_site(site_data, sites)

    cycle_data = format_country_results(cycle_data, product, country, aggregated_site)
    aggregated_cycle = update_cycle(country, start_year, end_year, source, functional_unit, False)(cycle_data)
    cycles = filter_min_score([
        calculate_score(aggregated_cycle, countries=[
            site.get('country', {}) for site in sites
        ] if multiple_countries else [])
    ])
    return (cycles, weights)


def aggregate_country(country: dict, product: dict, source: dict, start_year: int, end_year: int) -> list:
    init_covariance_files()

    # combine cycles into a "master" cycle with multiple values
    cycles = find_country_nodes(product, start_year, end_year, country)
    if not cycles:
        logger.info('1 - No cycles to run aggregation.')
        return []

    cycles_aggregated = aggregate_cycles(
        cycles=cycles,
        product=product,
        start_year=start_year,
        end_year=end_year
    )
    if not cycles_aggregated:
        logger.info('2 - No aggregated cycles.')
        return []

    logger.info('Cycles aggregated, generating final country aggregation...')
    log_memory_usage()

    functional_unit = cycles_aggregated[0].get('functionalUnit')
    include_matrix = aggregate_with_matrix(product)
    cycles_aggregated = non_empty_list([
        format_terms_results(cycle, product, country) for cycle in cycles_aggregated
    ])
    cycles_aggregated = non_empty_list(map(
        update_cycle(country, start_year, end_year, source, functional_unit, include_matrix),
        cycles_aggregated
    ))
    logger.info(f"Found {len(cycles_aggregated)} cycles at sub-country level")
    cycles_aggregated = filter_min_score(map(calculate_score, cycles_aggregated))
    if len(cycles_aggregated) == 0:
        logger.info('3 - No cycles to run aggregation.')
        return []

    # step 2: use aggregated cycles to calculate country-level cycles
    country_cycles, weights = _aggregate_country(
        country, product, cycles_aggregated, source, start_year, end_year,
        generate_weights_func=country_weights,
        missing_weights_node_id_func=country_weight_node_id
    ) if all([
        cycles_aggregated,
        # when not including matrix, cycles and country_cycles will be the same
        include_matrix
    ]) else ([], {})
    log_memory_usage()

    data = generate_covariance_country(weights=weights) if country_cycles else {}
    country_cycles = [v | data for v in country_cycles]

    log_memory_usage()

    remove_covariance_files()

    return cycles_aggregated + country_cycles


def aggregate_global(country: dict, product: dict, source: dict, start_year: int, end_year: int) -> list:
    """
    Aggregate World and other regions level 0 (like `region-easter-europe`).
    """
    cycles = find_global_nodes(product, start_year, end_year, country)
    cycles = [cycle | {'site': download_site(cycle.get('site'), data_state='original')} for cycle in cycles]

    aggregates, _weights = _aggregate_country(
        country, product, cycles, source, start_year, end_year,
        multiple_countries=True,
        generate_weights_func=world_weights,
        missing_weights_node_id_func=world_weight_node_id
    ) if cycles else ([], {})
    return aggregates


def run_aggregate(country: dict, product: dict, start_year: int, end_year: int, source: dict):
    aggregate_func = aggregate_global if _is_global(country) else aggregate_country
    return aggregate_func(country, product, source, start_year, end_year)
