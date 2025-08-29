from typing import List, Callable
from functools import reduce
from hestia_earth.utils.tools import non_empty_list, flatten, list_sum, list_average, is_boolean
from hestia_earth.utils.blank_node import get_node_value

from . import weighted_average, _min, _max, _sd, format_evs, pick
from .emission import get_method_tier
from .property import aggregate_properties
from .completeness import blank_node_completeness_key
from .distribution import sample_distributions


def _default_value_getter(node: dict, key: str, *args, **kwargs):
    return node.get(key)


def _weighted_value(weights: dict, key: str = 'value', value_getter=get_node_value):
    def apply(node: dict):
        value = value_getter(node, key, default=None)
        weight = weights.get(node.get('id'), {}).get('weight')
        return None if (value is None or weight is None) else (value, weight)
    return apply


def _missing_weights(blank_nodes: list, missing_weights_node_id_func):
    completeness_key = blank_node_completeness_key(blank_nodes[0])
    keys = list(map(missing_weights_node_id_func, blank_nodes))

    def apply(item: tuple):
        key, weight = item
        is_complete = weight.get('completeness', {}).get(completeness_key, False)
        is_missing = all([k not in key for k in keys])
        return (0, weight.get('weight')) if is_complete and is_missing else None
    return apply


def _product_rescale_ratio(nodes: list, weights: dict):
    all_weights = list_sum(non_empty_list([w.get('weight') for w in weights.values()]))
    node_weights = list_sum([weights.get(node.get('id'), {}).get('weight') for node in nodes])
    return node_weights / all_weights


def _aggregate(blank_nodes: list, weights: dict, missing_weights_node_id_func: Callable[[dict], str]):
    first_node = blank_nodes[0]
    node_type = first_node.get('@type') or first_node.get('type')
    term = first_node.get('term')

    # account for complete missing values
    missing_weights = non_empty_list(map(_missing_weights(blank_nodes, missing_weights_node_id_func), weights.items()))

    rescale_ratio = _product_rescale_ratio(blank_nodes, weights) if node_type == 'Product' else 1

    economicValueShare = weighted_average(
        non_empty_list(map(_weighted_value(weights, 'economicValueShare'), blank_nodes))
    )
    economicValueShare = economicValueShare * rescale_ratio if economicValueShare else None

    values_with_weight = non_empty_list(map(_weighted_value(weights), blank_nodes)) + missing_weights
    value = weighted_average(values_with_weight)
    values = [value * rescale_ratio for value, _w in values_with_weight]
    rescaled_value = value if is_boolean(value) else value * rescale_ratio if len(values) > 0 else None

    observations = sum(flatten([n.get('observations', 1) for n in blank_nodes])) + len(missing_weights)
    min_values = non_empty_list(flatten([n.get('min', []) for n in blank_nodes]))
    min_value = _min([v * rescale_ratio for v in min_values] + values, min_observations=1)
    max_values = non_empty_list(flatten([n.get('max', []) for n in blank_nodes]))
    max_value = _max([v * rescale_ratio for v in max_values] + values, min_observations=1)

    sd = _sd(values)

    inputs = flatten([n.get('inputs', []) for n in blank_nodes])
    properties = aggregate_properties(flatten([n.get('properties', []) for n in blank_nodes]))
    methodTier = get_method_tier(blank_nodes)

    distribution_weighted = non_empty_list(map(
        _weighted_value(weights, 'distribution', value_getter=_default_value_getter),
        blank_nodes
    ))
    distribution = sorted(flatten([
        sample_distributions(value, iteration_ratio=weight)
        for value, weight in distribution_weighted
    ]))

    primaryPercent = list_average(non_empty_list([v.get('primaryPercent') for v in blank_nodes]), default=None)

    return {
        'nodes': blank_nodes,
        'node': first_node,
        'term': term,
        'economicValueShare': format_evs(economicValueShare),
        'value': rescaled_value,
        'min': min_value,
        'max': max_value,
        'sd': sd,
        'observations': observations,
        'inputs': inputs,
        'properties': properties,
        'methodTier': methodTier,
        'primary': first_node.get('primary'),
        'primaryPercent': primaryPercent,
        'distribution': distribution
    } | pick(first_node, [
        'depthUpper', 'depthLower', 'startDate', 'endDate'
    ])


def _aggregate_term(aggregates_map: dict, weights: dict, missing_weights_node_id_func: Callable[[dict], str]):
    def aggregate(term_id: str):
        blank_nodes = [node for node in aggregates_map.get(term_id, []) if not node.get('deleted')]
        return _aggregate(blank_nodes, weights, missing_weights_node_id_func) if len(blank_nodes) > 0 else None
    return aggregate


def _aggregate_nodes(aggregate_keys: List[str], data: dict, weights: dict, missing_weights_node_id_func):
    def aggregate_single(key: str):
        aggregates_map: dict = data.get(key)
        terms = aggregates_map.keys()
        return non_empty_list(map(_aggregate_term(aggregates_map, weights, missing_weights_node_id_func), terms))

    return reduce(lambda prev, curr: prev | {curr: aggregate_single(curr)}, aggregate_keys, {})


def aggregate(
    aggregate_keys: List[str],
    data: dict,
    weights: dict,
    missing_weights_node_id_func: Callable[[dict], str]
) -> dict:
    return [] if weights is None else _aggregate_nodes(aggregate_keys, data, weights, missing_weights_node_id_func)
