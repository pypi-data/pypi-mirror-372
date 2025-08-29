from hestia_earth.schema import ManagementJSONLD
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.tools import safe_parse_date

from . import match_dates, _set_dict_single
from .queries import _get_time_ranges, _current_date


def new_management(data: dict):
    node = ManagementJSONLD().to_dict()
    node['term'] = linked_node(data.get('term'))

    value = data.get('value')
    if value is not None:
        node['value'] = value

    _set_dict_single(node, 'startDate', data.get('startDate'), strict=True)
    _set_dict_single(node, 'endDate', data.get('endDate'), strict=True)
    _set_dict_single(node, 'properties', data.get('properties'), strict=True)
    _set_dict_single(node, 'distribution', data.get('distribution'), strict=True)

    return node


def aggregated_dates(blank_node: dict):
    startDate = blank_node.get('startDate')
    endDate = blank_node.get('endDate')
    # when aggregating Management blank nodes, we use the nearest date in the 20 year period of aggregation
    time_ranges = _get_time_ranges(startDate or endDate, endDate) if endDate else []
    # use the latest time range that encompass the `endDate`
    time_range = time_ranges[-1] if time_ranges else None
    current_date = _current_date()
    is_current_year = time_range[1] == int(current_date[:4]) if time_range else False
    return {
        'startDate': f"{time_range[0]}-01-01",
        'endDate': current_date if is_current_year else f"{time_range[1]}-12-31"
    } if time_ranges else {}


def filter_management(blank_nodes: list, start_year: int = None, end_year: int = None):
    def update_dates(blank_node: dict):
        start_date = safe_parse_date(blank_node.get('startDate'), default=None)
        end_date = safe_parse_date(blank_node.get('endDate'), default=None)

        return blank_node | (
            {'startDate': f"{start_year - 20}-01-01"}
            if start_year and start_date and start_date.year < (start_year - 20) else {}
        ) | (
            {'endDate': f"{end_year}-12-31"}
            if end_year and end_date and end_date.year > end_year else {}
        )

    """
    Filter management blank nodes to only return the current period + 20years prior period.
    Every management that overlaps with the time range will have the date updated so it does not overlap anymore.
    """
    return [
        update_dates(v) for v in blank_nodes
        if not start_year or not end_year or match_dates(v, start_year - 20, end_year)
    ]
