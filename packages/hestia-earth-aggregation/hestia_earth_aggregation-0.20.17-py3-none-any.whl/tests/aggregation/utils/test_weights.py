from hestia_earth.aggregation.utils.weights import _country_irrigated_weight, _irrigated_weight

country_id = 'GADM-ECU'


def test_country_irrigated_weight():
    assert round(_country_irrigated_weight(country_id, 2010, 2019, 'Agriculture'), 2) == 0.15


def test_irrigated_weight():
    assert round(_irrigated_weight(country_id, 2010, 2019), 2) == 0.35
