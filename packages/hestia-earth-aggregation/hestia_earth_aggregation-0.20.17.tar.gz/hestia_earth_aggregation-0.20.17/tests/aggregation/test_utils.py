from hestia_earth.aggregation.utils import _aggregated_node, _aggregated_version


def test_aggregated_node():
    node = {'value': 10}
    assert _aggregated_node(node)['aggregated'] is True


def test_aggregated_version():
    node = {'value': 10}
    assert _aggregated_version(node)['aggregated'] == ['value']
