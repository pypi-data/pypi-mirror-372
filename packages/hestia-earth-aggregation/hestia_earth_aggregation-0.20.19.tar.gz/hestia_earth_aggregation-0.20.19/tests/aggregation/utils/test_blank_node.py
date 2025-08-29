from hestia_earth.aggregation.utils.blank_node import default_missing_value


def test_default_missing_value():
    term = {'@id': 'inorganicNitrogenFertiliserUsed', 'termType': 'landUseManagement'}
    assert not default_missing_value(term)
