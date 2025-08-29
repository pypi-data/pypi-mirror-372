import os
import json
from decimal import Decimal
from statistics import stdev, mean
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.tools import non_empty_list, flatten, safe_parse_date

from ..version import VERSION

MIN_NB_OBSERVATIONS = 20
CYCLE_AGGREGATION_KEYS = ['inputs', 'practices', 'products', 'emissions']
SITE_AGGREGATION_KEYS = ['measurements', 'management']


class HestiaError(Exception):
    def __init__(self, message: str, data: dict = {}):
        super().__init__(message)
        self.error = {'message': message} | data

    def __str__(self):
        return f"Error downloading nodes: {json.dumps(self.error or {})}"


def create_folders(filepath: str): return os.makedirs(os.path.dirname(filepath), exist_ok=True)


def pick(value: dict, keys: list): return {k: value.get(k) for k in keys if k in value}


def is_empty(value):
    return value is None or (
        value in [None, '', '-'] if isinstance(value, str) else
        len(value) == 0 if isinstance(value, list) else
        len(value.keys()) == 0 if isinstance(value, dict) else
        False
    )


def remove_empty_fields(value: dict):
    return {key: value for key, value in value.items() if not is_empty(value)}


def _save_json(data: dict, filename: str):
    should_run = os.getenv('DEBUG', 'false') == 'true'
    if not should_run:
        return
    dir = os.getenv('TMP_DIR', '/tmp')
    filepath = f"{dir}/{filename}.jsonld"
    create_folders(filepath)
    with open(filepath, 'w') as f:
        return json.dump(data, f, indent=2)


def sum_data(nodes: list, key: str): return sum([node.get(key, 1) for node in nodes])


def format_aggregated_list(node_type: str, values: list):
    nodes = non_empty_list(flatten([
        {'@id': v} if isinstance(v, str) else v.get(f"aggregated{node_type}s")
        for v in non_empty_list(values)
    ]))
    # build sorted list of ids
    ids = sorted(list(set(map(lambda x: x['@id'], nodes))))
    nodes = [{'@type': node_type, '@id': v} for v in ids]
    return list(map(linked_node, nodes))


def match_dates(blank_node: dict, start_year: int, end_year: int):
    dates = blank_node.get('dates', [])
    start_date = safe_parse_date(blank_node.get('startDate'), default=None)
    end_date = safe_parse_date(blank_node.get('endDate'), default=None)
    return all([
        not dates or any([
            int(start_year) <= safe_parse_date(date).year <= int(end_year)
            for date in dates
            if safe_parse_date(date, default=None)
        ]),
        not start_date or not end_date or any([
            int(start_year) <= start_date.year <= int(end_year),
            int(start_year) <= end_date.year <= int(end_year)
        ])
    ])


def _aggregated_node(node: dict):
    return node | {'aggregated': True, 'aggregatedVersion': VERSION}


def _aggregated_version(node: dict):
    keys = list(node.keys())
    keys.remove('@type') if '@type' in keys else None
    node['aggregated'] = node.get('aggregated', [])
    node['aggregatedVersion'] = node.get('aggregatedVersion', [])
    for key in keys:
        if node.get(key) is None:
            continue
        if key in node['aggregated']:
            node.get('aggregatedVersion')[node['aggregated'].index(key)] = VERSION
        else:
            node['aggregated'].append(key)
            node['aggregatedVersion'].append(VERSION)
    return node


def _min(values, observations: int = 0, min_observations: int = MIN_NB_OBSERVATIONS):
    has_boolean = any([isinstance(v, bool) for v in values])
    return None if has_boolean else min(values) if (observations or len(values)) >= min_observations else None


def _max(values, observations: int = 0, min_observations: int = MIN_NB_OBSERVATIONS):
    has_boolean = any([isinstance(v, bool) for v in values])
    return None if has_boolean else max(values) if (observations or len(values)) >= min_observations else None


def _sd(values): return stdev(values) if len(values) >= 2 else None


def _all_boolean(values: list): return all([isinstance(v, bool) for v in values])


def _numeric_weighted_average(values: list):
    total_weight = sum(Decimal(str(weight)) for _v, weight in values) if values else Decimal(0)
    weighted_values = [Decimal(str(value)) * Decimal(str(weight)) for value, weight in values]
    average = sum(weighted_values) / (total_weight if total_weight else 1) if weighted_values else None
    return None if average is None else float(average)


def _bool_weighted_average(values: list):
    return mean(map(int, values)) >= 0.5


def weighted_average(weighted_values: list):
    values = [v for v, _w in weighted_values]
    all_boolean = _all_boolean(values)
    return None if not values else (
        _bool_weighted_average(values) if all_boolean else _numeric_weighted_average(weighted_values)
    )


def _unique_nodes(nodes: list):
    return sorted(list({n.get('@id'): n for n in nodes}.values()), key=lambda n: n.get('@id'))


def _set_dict_single(data: dict, key: str, value, strict=False):
    if value is not None and (not strict or not is_empty(value)):
        data[key] = value
    return data


def _set_dict_array(data: dict, key: str, value, strict=False):
    if data is not None and value is not None and (not strict or value != 0):
        data[key] = [value]
    return data


def format_evs(value: float): return min([100, round(value, 2)]) if value else value


def value_difference(value: float, expected_value: float):
    """
    Get the difference in percentage between a value and the expected value.

    Parameters
    ----------
    value : float
        The value to check.
    expected_value : float
        The expected value.

    Returns
    -------
    bool
        The difference in percentage between the value and the expected value.
    """
    return 0 if (isinstance(expected_value, list) and len(expected_value) == 0) or expected_value == 0 else (
        round(abs(value - expected_value) / expected_value, 4)
    )
