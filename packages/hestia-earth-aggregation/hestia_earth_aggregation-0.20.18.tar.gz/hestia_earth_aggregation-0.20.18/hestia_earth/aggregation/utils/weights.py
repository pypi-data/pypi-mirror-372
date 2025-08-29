from functools import reduce
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name

from hestia_earth.aggregation.log import debugWeights, debugRequirements
from .lookup import production_quantity_lookup, production_quantity_country, lookup_data_period_average
from .term import DEFAULT_COUNTRY_ID, _format_organic, _format_irrigated, _format_country_name


def _country_organic_weight(country_id: str, start_year: int, end_year: int):
    lookup = download_lookup('region-standardsLabels-isOrganic.csv')
    data = get_table_value(lookup, 'termid', country_id, 'organic')
    # default to 0 => assume nothing organic
    value = lookup_data_period_average(data, start_year, end_year, default=0)

    debugRequirements(country_id=country_id, start_year=start_year, end_year=end_year,
                      organic_weight=value)

    return min(1, value / 100) if value else None


_IRRIGATED_COLUMN_MAPPING = {
    'Agriculture irrigated': 'Agriculture area actually irrigated',
    'Cropland irrigated': 'Cropland area actually irrigated',
    'Land area irrigated': 'Land area equipped for irrigation'
}


def _country_irrigated_weight(country_id: str, start_year: int, end_year: int, siteType: str = 'Land area'):
    lookup = download_lookup('region-irrigated.csv')

    total_area_data = get_table_value(lookup, 'termid', country_id, column_name(siteType))
    # default to 1 => assume whole area
    total_area = lookup_data_period_average(total_area_data, start_year, end_year, default=1)

    irrigated_column_name = _IRRIGATED_COLUMN_MAPPING.get(f"{siteType} irrigated")
    irrigated_data = (
        get_table_value(lookup, 'termid', country_id, column_name(irrigated_column_name)) or
        get_table_value(lookup, 'termid', country_id, column_name(f"{siteType} irrigated"))
    )
    irrigated = lookup_data_period_average(irrigated_data, start_year, end_year)

    debugRequirements(country_id=country_id, start_year=start_year, end_year=end_year,
                      site_type=siteType,
                      total_area=total_area,
                      irrigated_area=irrigated)

    return irrigated / total_area if irrigated else None


def _irrigated_weight(country_id: str, start_year: int, end_year: int):
    return (
        _country_irrigated_weight(country_id, start_year, end_year, 'Cropland') or
        _country_irrigated_weight(country_id, start_year, end_year, 'Agriculture') or
        _country_irrigated_weight(country_id, start_year, end_year, 'all') or
        _country_irrigated_weight(country_id, start_year, end_year)
    )


def _country_weights(country_id: str, start_year: int, end_year: int, node: dict, completeness: dict) -> dict:
    node_id = node.get('@id', node.get('id'))
    organic_weight = (
        _country_organic_weight(country_id, start_year, end_year) or
        _country_organic_weight(DEFAULT_COUNTRY_ID, start_year, end_year) or
        0
    )
    irrigated_weight = _irrigated_weight(country_id, start_year, end_year) or 0
    weight = (
        organic_weight if node.get('organic', False) else 1-organic_weight
    ) * (
        irrigated_weight if node.get('irrigated', False) else 1-irrigated_weight
    )
    return {node_id: {'weight': weight, 'completeness': completeness}}


def country_weights(data: dict):
    nodes = data.get('nodes')
    country_id = data.get('country').get('@id')
    start_year = data.get('start_year')
    end_year = data.get('end_year')
    completeness = data.get('node-completeness')
    weights = reduce(
        lambda prev, curr: prev | _country_weights(country_id, start_year, end_year, curr[1], completeness[curr[0]]),
        enumerate(nodes),
        {}
    )
    debugWeights(weights)
    return weights


def country_weight_node_id(blank_node: dict):
    return '-'.join([_format_organic(blank_node.get('organic')), _format_irrigated(blank_node.get('irrigated'))])


def _world_weight(lookup, lookup_column: str, country_id: str, start_year: int, end_year: int):
    country_value = production_quantity_country(lookup, lookup_column, start_year, end_year, country_id) or 1
    world_value = production_quantity_country(lookup, lookup_column, start_year, end_year) or 1
    return min(1, country_value / world_value)


def _world_weights(lookup, lookup_column, node: dict, completeness: dict) -> dict:
    node_id = node.get('@id', node.get('id'))
    country_id = node.get('country').get('@id')
    start_year = node.get('start_year')
    end_year = node.get('end_year')
    weight = _world_weight(lookup, lookup_column, country_id, start_year, end_year) if lookup is not None else 1
    return {node_id: {'weight': weight, 'completeness': completeness}}


def world_weights(data: dict) -> dict:
    nodes = data.get('nodes', [])
    completeness = data.get('node-completeness')
    lookup, lookup_column = production_quantity_lookup(data.get('product'))
    weights = reduce(
        lambda prev, curr: prev | _world_weights(lookup, lookup_column, curr[1], completeness[curr[0]]),
        enumerate(nodes),
        {}
    )
    debugWeights(weights)
    # make sure we have at least one value with `weight`, otherwise we cannot generate an aggregated value
    no_weights = next((v for v in weights.values() if v.get('weight', 0) > 0), None) is None
    return None if no_weights else weights


def world_weight_node_id(blank_node: dict):
    return _format_country_name(blank_node)
