import pytest
from hestia_earth.schema import TermTermType

from hestia_earth.aggregation.utils.aggregate_country_nodes import _combine_blank_nodes_stats, _compute_blank_node_stats

class_path = 'hestia_earth.aggregation.utils.aggregate_country_nodes'

_BLANK_NODES = [
    {
       'value': [1.04], 'min': [0.6], 'max': [2], 'sd': [0.6]
    }, {
       'value': [4.55], 'min': [], 'max': [7], 'sd': [0.1]
    }, {
       'value': [1.76], 'min': [0.3], 'max': [], 'sd': [0.3]
    }, {
       'value': [0.99], 'min': [0.2], 'max': [5], 'sd': []
    }, {
       'value': [0.123], 'min': [], 'max': [1], 'sd': []
    }, {
       'value': [1, 2], 'min': [0.1, 0.15], 'max': [3, 4], 'sd': [0.7, 0.8]
    }
]


@pytest.mark.parametrize(
    'term,expected',
    [
        (
            {'termType': TermTermType.SEED.value, '@id': 'seed'},
            {
                'value': 11.463,
                'min': 6.023,
                'max': 23.76,
                'sd': 1.741,
                'observations': 1
            }
        ),
        (
            {'termType': TermTermType.MEASUREMENT.value, '@id': 'sandContent'},
            {
                'value': 1.66,
                'min': 0.123,
                'max': 7,
                'sd': 0.295,
                'observations': 1
            }
        )
    ]
)
def test_compute_blank_node_stats(term: dict, expected: dict):
    blank_node = _combine_blank_nodes_stats([
        v | {'term': term} for v in _BLANK_NODES
    ])
    result = _compute_blank_node_stats(blank_node | {'term': term})
    assert {k: round(v, 3) for k, v in result.items()} == expected
