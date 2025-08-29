import os
from enum import Enum
from functools import reduce
from hestia_earth.schema import SchemaType, TermTermType, AGGREGATED_QUALITY_SCORE_FIELDS
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.tools import list_sum, non_empty_list
from hestia_earth.utils.emission import cycle_emission_is_in_system_boundary, cycle_emissions_in_system_boundary

from hestia_earth.aggregation.log import debugRequirements, logger
from . import value_difference
from .blank_node import get_lookup_value
from .lookup import production_quantity_lookup, production_quantity_country, lookup_data_period_average
from .term import should_aggregate

KEY = 'aggregatedQualityScore'
KEY_MAX = KEY + 'Max'
_FAOSTAT_PRODUCTION_LOOKUP_COLUMN = 'cropGroupingFaostatProduction'
_YIELD_THRESHOLD = 20
_REGION_PRODUCTION_THRESHOLD = 75
_COMPLETENESS_SCORE_FIELDS = AGGREGATED_QUALITY_SCORE_FIELDS.get(SchemaType.COMPLETENESS.value, {})
_MIN_NB_OBSERVATIONS = {
    'default': 50,
    TermTermType.PROCESSEDFOOD.value: 10
}


class ScoreKeys(Enum):
    YIELD = 'yield'
    NB_CYCLES = 'nb_cycles'
    COMPLETENESS = 'completeness'
    EMISSIONS_SYSTEM_BOUNDARY = 'emissions_system_boundary'
    REGION_PRODUCTION_RATIO = 'countries_production_ratio'


def _faostat_crop_yield(country_id: str, grouping: str, start_year: int, end_year: int):
    lookup = download_lookup(f"region-crop-{_FAOSTAT_PRODUCTION_LOOKUP_COLUMN}-yield.csv")
    value = get_table_value(lookup, 'termid', country_id, column_name(grouping))
    value = lookup_data_period_average(value, start_year, end_year)
    logger.debug(f"FAOSTAT yield for {grouping} in {country_id}: {value}")
    # value in lookup is in kg/ha
    return round(value, 4) if value is not None else None


def _calculate_score_yield(cycle: dict, primary_product: dict, *args):
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    start_year = int(cycle.get('startDate'))
    end_year = int(cycle.get('endDate'))
    grouping = get_lookup_value(primary_product.get('term', {}), _FAOSTAT_PRODUCTION_LOOKUP_COLUMN)
    faostat_yield = _faostat_crop_yield(country_id, grouping, start_year, end_year) if grouping else None
    product_yield = list_sum(primary_product.get('value')) if primary_product else None
    delta = value_difference(product_yield, faostat_yield) * 100 if all([faostat_yield, product_yield]) else None

    debugRequirements(id=cycle.get('id'),
                      country_id=country_id,
                      start_year=start_year,
                      end_year=end_year,
                      faostat_grouping=grouping,
                      faostat_yield=faostat_yield,
                      product_yield=product_yield,
                      yield_delta=delta,
                      yield_delta_min=_YIELD_THRESHOLD,
                      yield_delta_threshold=_YIELD_THRESHOLD)

    return delta <= _YIELD_THRESHOLD if delta is not None else False


def _production_delta(cycle: dict, countries: list, lookup, lookup_column: str):
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    start_year = int(cycle.get('startDate'))
    end_year = int(cycle.get('endDate'))
    global_value = production_quantity_country(lookup, lookup_column, start_year, end_year, country_id=country_id)
    country_values = non_empty_list([
        production_quantity_country(lookup, lookup_column, start_year, end_year, country_id=country.get('@id'))
        for country in countries
    ])
    total_value = list_sum(country_values)
    delta = (total_value / global_value) * 100 if global_value and total_value else None

    debugRequirements(id=cycle.get('id'),
                      country_id=country_id,
                      start_year=start_year,
                      end_year=end_year,
                      region_production_quantity=global_value,
                      countries_production_quantity=total_value,
                      production_delta=delta,
                      production_delta_min=_REGION_PRODUCTION_THRESHOLD)

    return delta


def _calculate_score_region_production(cycle: dict, primary_product: dict, countries: list):
    term = primary_product.get('term', {})
    lookup, lookup_column = production_quantity_lookup(term)
    delta = _production_delta(cycle, countries, lookup, lookup_column) if lookup is not None else None
    return delta >= _REGION_PRODUCTION_THRESHOLD if delta is not None else False


def _calculate_score_nb_cycles(cycle: dict, primary_product: dict, *args):
    term_type = primary_product.get('term', {}).get('termType')
    min_nb_observations = _MIN_NB_OBSERVATIONS.get(term_type) or _MIN_NB_OBSERVATIONS.get('default')
    nb_observations = cycle.get('numberOfCycles', 1)

    debugRequirements(id=cycle.get('id'),
                      nb_observations=nb_observations,
                      min_nb_observations=min_nb_observations)

    return nb_observations >= min_nb_observations


def _calculate_score_completeness(cycle: dict, primary_product: dict, *args):
    term_type = primary_product.get('term', {}).get('termType')
    completeness_fields = _COMPLETENESS_SCORE_FIELDS.get(term_type, [])
    completeness: dict = cycle.get('completeness', {})
    completeness_keys = [k for k in completeness.keys() if k in completeness_fields]
    is_complete = all([bool(completeness.get(k)) for k in completeness_keys])
    incomplete_keys = [k for k in completeness_keys if not bool(completeness.get(k))]

    debugRequirements(id=cycle.get('id'),
                      is_complete=is_complete,
                      completeness_keys=';'.join(completeness_keys),
                      incomplete_keys=';'.join(incomplete_keys))

    return is_complete


def _calculate_score_emissions_system_boundary(cycle: dict, *args):
    # get all emissions in the system boundary
    all_emissions_ids = cycle_emissions_in_system_boundary(cycle)
    # ignore emissions that have `skipAggregation=true`
    all_emissions_ids = list(filter(lambda id: should_aggregate({
        '@id': id, 'termType': TermTermType.EMISSION.value
    }), all_emissions_ids))

    # get all emissions in the Cycle that are in the system boundary
    emissions_ids = list(filter(
        cycle_emission_is_in_system_boundary(cycle),
        list(set([e.get('term', {}).get('@id') for e in cycle.get('emissions', [])]))
    ))

    missing_emissions = list(filter(lambda term_id: term_id not in emissions_ids, all_emissions_ids))
    all_included = len(missing_emissions) == 0

    debugRequirements(id=cycle.get('id'),
                      total_emissions_in_system_boundary=len(all_emissions_ids),
                      included_emissions=len(emissions_ids),
                      all_included=all_included,
                      missing_emissions=';'.join(missing_emissions))

    return all_included


_FUNC_SCORE_KEY = {
    ScoreKeys.YIELD: _calculate_score_yield,
    ScoreKeys.COMPLETENESS: _calculate_score_completeness,
    ScoreKeys.EMISSIONS_SYSTEM_BOUNDARY: _calculate_score_emissions_system_boundary,
    ScoreKeys.NB_CYCLES: _calculate_score_nb_cycles,
    ScoreKeys.REGION_PRODUCTION_RATIO: _calculate_score_region_production,
}


def _should_run_crop(cycle: dict, *args):
    product = find_primary_product(cycle)
    term = (product or {}).get('term', {})
    return term.get('termType') == TermTermType.CROP.value


_RUN_SCORE_KEY = {
    ScoreKeys.YIELD: _should_run_crop,
    ScoreKeys.REGION_PRODUCTION_RATIO: lambda cycle, countries: len(countries) > 0 and _should_run_crop(cycle)
}


def calculate_score(cycle: dict, countries: list = []):
    product = find_primary_product(cycle) or {}
    score_keys = [e for e in ScoreKeys if _RUN_SCORE_KEY.get(e, lambda *args: True)(cycle, countries)]
    score = reduce(
        lambda total, key: total + (1 if _FUNC_SCORE_KEY.get(key)(cycle, product, countries) else 0), score_keys, 0
    )
    return {
        **cycle,
        KEY: score,
        KEY_MAX: len(score_keys)
    }


def _enable_filter_min_score(): return os.getenv('AGGREGATION_MAX_SCORE_ENABLED', 'false') == 'true'


def _min_score_diff(): return int(os.getenv('AGGREGATION_MAX_SCORE_DIFF', '2'))


def has_min_score(data: dict):
    # aggregation is only valid if score is more than max-2 by default
    return all([
        # if ImpactAssessment is created without a Cycle, this will ignore the IA.
        data.get(KEY, 0) >= 0,
        data.get(KEY_MAX, 0) - data.get(KEY, 0) <= _min_score_diff()
    ])


def filter_min_score(values: list):
    return list(filter(has_min_score, values)) if _enable_filter_min_score() else list(values)
