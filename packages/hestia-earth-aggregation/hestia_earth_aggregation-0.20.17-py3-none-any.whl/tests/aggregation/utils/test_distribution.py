import pytest
from statistics import mean
from hestia_earth.schema import TermTermType

from hestia_earth.aggregation.utils.distribution import (
    ITERATIONS,
    generate_distribution,
    sample_distributions,
    _distribute_iterations
)

_term = {'termType': TermTermType.MEASUREMENT.value, '@id': 'sandContent'}


@pytest.mark.parametrize(
    'value,sd,min,max',
    [
        (10, None, None, None),
        (10, 1, None, None),
        (10, 1, 5, None),
        (10, 1, None, 15),
        (10, None, 5, None),
        (10, None, None, 15),
        (0, None, None, None),
        (10, 0.1, 10, 10)
    ]
)
def test_generate_distribution(value: float, sd: float, min: float, max: float):
    results = generate_distribution(_term, value=value, min=min, max=max, sd=sd)
    assert len(results) == ITERATIONS
    assert 0.90*value <= mean(results) <= 1.1*value


def test_sample_distributions():
    distributions = list(generate_distribution(_term, value=10)) * 10
    assert len(sample_distributions(distributions)) == ITERATIONS


def test_distribute_iterations():
    assert _distribute_iterations([1] * 2, iterations=2) == [1, 1]
    assert _distribute_iterations([1] * 2, iterations=3) == [2, 1]
    assert _distribute_iterations([1] * 4, iterations=10) == [3, 3, 2, 2]
    assert _distribute_iterations([1] * 60, iterations=100) == [2] * 40 + [1] * 20
