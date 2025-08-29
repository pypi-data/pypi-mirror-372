import os
import json
import pytest
from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.model import find_primary_product

from tests.utils import fixtures_path
from hestia_earth.aggregation.utils.quality_score import (
    KEY, KEY_MAX, has_min_score,
    calculate_score,
    _faostat_crop_yield,
    _calculate_score_yield,
    _calculate_score_completeness,
    _calculate_score_nb_cycles,
    _calculate_score_emissions_system_boundary,
    _calculate_score_region_production,
)

fixtures_folder = os.path.join(fixtures_path, 'utils', KEY)


def test_has_min_score():
    assert has_min_score({}) is True

    cycle = {
        KEY: 2,
        KEY_MAX: 5
    }
    assert not has_min_score(cycle)

    cycle = {
        KEY: 3,
        KEY_MAX: 5
    }
    assert has_min_score(cycle) is True

    cycle = {
        KEY: 5,
        KEY_MAX: 5
    }
    assert has_min_score(cycle) is True


def test_calculte_score():
    with open(os.path.join(fixtures_folder, 'crop.jsonld'), encoding='utf-8') as f:
        cycle = json.load(f)

    result = calculate_score(cycle)
    assert result.get(KEY) == 2
    assert result.get(KEY + 'Max') == 4

    with open(os.path.join(fixtures_folder, 'animalProduct.jsonld'), encoding='utf-8') as f:
        cycle = json.load(f)

    result = calculate_score(cycle)
    assert result.get(KEY) == 0
    assert result.get(KEY + 'Max') == 3


def test_faostat_crop_yield():
    assert round(_faostat_crop_yield('region-world', 'Maize (corn)', 2000, 2009)) == 4772
    assert _faostat_crop_yield('GADM-IND', 'Maize (corn)', 2000, 2024) == 2498.4417
    assert _faostat_crop_yield('GADM-ESP', 'Mushrooms and truffles', 2000, 2019) is None


def test_calculate_score_yield():
    product = {
        'primary': True,
        'term': {'termType': 'crop', '@id': 'maizeGrain'},
        'value': [
            4500
        ]
    }
    cycle = {
        'site': {'country': {'@id': 'region-world'}},
        'startDate': 2000,
        'endDate': 2009,
        'products': [product]
    }

    assert _calculate_score_yield(cycle, product) is True

    cycle = {
        'site': {'country': {'@id': 'GADM-ESP'}},
        'startDate': 2010,
        'endDate': 2019,
        'products': [{
            'primary': True,
            'term': {'termType': 'crop', '@id': 'agaricusBisporusFruitingBody'},
            'value': [
                1
            ]
        }]
    }

    assert _calculate_score_yield(cycle, product) is False


@pytest.mark.parametrize(
    'filename,expected',
    [
        ('complete', True),
        ('incomplete', False),
        ('animalProduct', False),
        ('crop', False),
        ('processedFood', True),
    ]
)
def test_calculate_score_completeness(filename: str, expected: bool):
    with open(os.path.join(fixtures_folder, f"{filename}.jsonld"), encoding='utf-8') as f:
        cycle = json.load(f)

    assert _calculate_score_completeness(cycle, find_primary_product(cycle)) == expected


@pytest.mark.parametrize(
    'filename,expected',
    [
        ('complete', True),
        ('incomplete', False),
        ('animalProduct', False),
        ('crop', True),
        ('processedFood', True),
    ]
)
def test_calculate_score_nb_cycles(filename: str, expected: bool):
    with open(os.path.join(fixtures_folder, f"{filename}.jsonld"), encoding='utf-8') as f:
        cycle = json.load(f)

    assert _calculate_score_nb_cycles(cycle, find_primary_product(cycle)) == expected


def test_calculate_score_emissions_system_boundary():
    cycle = {
        'site': {'siteType': SiteSiteType.CROPLAND.value},
        'products': [{'primary': True, 'term': {'termType': 'crop', '@id': 'wheatGrain'}}]
    }

    assert not _calculate_score_emissions_system_boundary(cycle)


def test_calculate_score_region_production():
    product = {'primary': True, 'term': {'termType': 'crop', '@id': 'wheatGrain'}}
    cycle = {
        'site': {'country': {'@id': 'region-world'}},
        'startDate': '1990',
        'endDate': '2000',
        'products': [product]
    }

    countries = [
        {'@id': 'GADM-FRA'},
        {'@id': 'GADM-GBR'}
    ]
    cycle['site']['country']['@id'] = 'region-world'
    assert not _calculate_score_region_production(cycle, product, countries)

    cycle['site']['country']['@id'] = 'region-northern-europe'
    assert _calculate_score_region_production(cycle, product, countries) is True

    countries = [
        {'@id': 'GADM-BRA'},
        {'@id': 'GADM-CAN'},
        {'@id': 'GADM-CHN'},
        {'@id': 'GADM-DNK'},
        {'@id': 'GADM-EGY'},
        {'@id': 'GADM-ETH'},
        {'@id': 'GADM-FIN'},
        {'@id': 'GADM-FRA'},
        {'@id': 'GADM-DEU'},
        {'@id': 'GADM-GBR'},
        {'@id': 'GADM-GRC'},
        {'@id': 'GADM-IND'},
        {'@id': 'GADM-IRN'},
        {'@id': 'GADM-ITA'},
        {'@id': 'GADM-MEX'},
        {'@id': 'GADM-POL'},
        {'@id': 'GADM-RUS'},
        {'@id': 'GADM-SWE'},
        {'@id': 'GADM-TUR'},
        {'@id': 'GADM-USA'}
    ]
    cycle['site']['country']['@id'] = 'region-world'
    assert _calculate_score_region_production(cycle, product, countries) is True

    cycle['site']['country']['@id'] = 'region-northern-europe'
    assert _calculate_score_region_production(cycle, product, countries) is True
