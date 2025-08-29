import pytest
from unittest.mock import patch
from hestia_earth.schema import TermTermType

from hestia_earth.aggregation.utils.term import _fetch_all, _format_country_name

class_path = 'hestia_earth.aggregation.utils.term'


@patch(f"{class_path}.find_node", return_value=[])
def test_fetch_all(mock_find_node):
    _fetch_all(TermTermType.EMISSION)
    mock_find_node.assert_called_once()


@pytest.mark.parametrize(
    'name,expected',
    [
        ('Virgin Islands, U.S.', 'virgin-islands-us'),
        ('Turkey (Country)', 'turkey-country'),
        ("Côte d'Ivoire", 'cote-divoire'),
        ('Åland', 'aland'),
        ('Réunion', 'reunion'),
        ('São Tomé and Príncipe', 'sao-tome-and-principe')
    ]
)
def test_format_country_name(name: str, expected: str):
    assert _format_country_name({'country': {'name': name}}) == expected, name
