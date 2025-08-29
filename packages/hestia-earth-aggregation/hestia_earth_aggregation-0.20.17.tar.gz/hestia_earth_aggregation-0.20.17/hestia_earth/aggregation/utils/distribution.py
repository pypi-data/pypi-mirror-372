import os
from typing import List
from hestia_earth.utils.stats import truncated_normal_1d
from hestia_earth.utils.tools import flatten
import random
import numpy as np

from . import _all_boolean
from .blank_node import get_lookup_value

ITERATIONS = int(os.getenv('AGGREGATION_DISTRIBUTION_SIZE', '1000'))


def _sample_values(values: List[float], nb_iterations: int = ITERATIONS): return random.sample(values, nb_iterations)


def _sample_indexes(values: list): return [random.sample(range(len(values)), 1)[0] for _ in range(ITERATIONS)]


def _distribute_iterations(values: list, iterations: int = ITERATIONS):
    num_iterations = int(iterations / len(values))
    total_iterations = len(values) * num_iterations
    remaining_iterations = iterations - total_iterations
    return [num_iterations + 1] * remaining_iterations + [num_iterations] * (len(values) - remaining_iterations)


def generate_distribution(
    term: dict, *_, value: float, min: float = None, max: float = None, sd: float = None, iterations: int = ITERATIONS
):
    has_min_value = all([min is not None, min != value])
    min_bound = min if has_min_value else get_lookup_value(term, 'minimum')
    min_bound = -np.inf if min_bound is None else min_bound

    has_max_value = all([max is not None, max != value])
    max_bound = max if has_max_value else get_lookup_value(term, 'maximum')
    max_bound = np.inf if max_bound is None else max_bound

    result = [] if isinstance(value, bool) else list(
        (
            truncated_normal_1d(shape=(1, iterations), mu=value, sigma=sd or (max-min)/4, low=min, high=max) if all([
                has_min_value,
                has_max_value
            ]) else
            truncated_normal_1d(shape=(1, iterations), mu=value, sigma=sd, low=min_bound, high=max_bound) if all([
                sd is not None
            ]) else
            [[value] * iterations]
        )[0]
    ) if value is not None else []
    return result


def _generate_blank_node_distribution_random_iterations(blank_node: dict):
    # generate distribution, by using random indexes
    # this method is only called when the number of values is greater than the number of iterations
    value = blank_node.get('value', [])
    random_indexes = _sample_indexes(value)

    def _value_at_index(index: int, key: str):
        values = blank_node.get(key) or []
        try:
            return values[index]
        # TODO catch only IndexError, and figure out why `sd` is a float instead of a list
        except Exception:
            return None

    return flatten([
        generate_distribution(
            term=blank_node['term'],
            value=_value_at_index(index, 'value'),
            min=_value_at_index(index, 'min'),
            max=_value_at_index(index, 'max'),
            sd=_value_at_index(index, 'sd'),
            iterations=1
        )
        for index in random_indexes
    ])


def _generate_blank_node_distribution_distributed_iterations(blank_node: dict):
    # generate distributions equally distributed across the different values
    # this mthod is only called when the number of values is smaller than the number of iterations
    value = blank_node.get('value', [])

    def _value_at_index(index: int, key: str):
        values = blank_node.get(key) or []
        try:
            return values[index]
        # TODO catch only IndexError, and figure out why `sd` is a float instead of a list
        except Exception:
            return None

    iterations = _distribute_iterations(value)

    return flatten([
        generate_distribution(
            term=blank_node['term'],
            value=_value_at_index(index, 'value'),
            min=_value_at_index(index, 'min'),
            max=_value_at_index(index, 'max'),
            sd=_value_at_index(index, 'sd'),
            iterations=iterations[index]
        )
        for index in range(0, len(value))
    ])


def generate_blank_node_distribution(blank_node: dict):
    value = blank_node.get('value', [])
    return (
        _generate_blank_node_distribution_random_iterations(blank_node) if len(value) >= ITERATIONS else
        _generate_blank_node_distribution_distributed_iterations(blank_node)
    )


def sample_distributions(
    distributions: List[List[float]],
    total_iterations: int = ITERATIONS,
    iteration_ratio: float = 1.0
):
    values = flatten(distributions)
    nb_iterations = round(total_iterations * iteration_ratio)
    return (
        [] if _all_boolean(values) else
        values if len(values) <= nb_iterations else
        _sample_values(values, nb_iterations)
    )
