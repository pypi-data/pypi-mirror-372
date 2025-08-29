import re
from unidecode import unidecode
from typing import Union
from functools import lru_cache
from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.model import linked_node, find_term_match
from hestia_earth.utils.api import find_node, find_node_exact, download_hestia
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import safe_parse_float

SEARCH_LIMIT = 10000
DEFAULT_COUNTRY_ID = 'region-world'
DEFAULT_COUNTRY_NAME = 'World'
DEFAULT_COUNTRY = {'@id': 'region-world', 'name': DEFAULT_COUNTRY_NAME}
MODEL = 'aggregatedModels'
METHOD_MODEL = {'@type': SchemaType.TERM.value, '@id': MODEL}
DRY_MATTER_TERM_ID = 'dryMatter'


def _fetch_all(term_type: TermTermType): return find_node(SchemaType.TERM, {'termType': term_type.value}, SEARCH_LIMIT)


@lru_cache()
def get_by_name(value: str): return find_node_exact(SchemaType.TERM, {'name': value})


@lru_cache()
def get_by_id(value: str): return find_node_exact(SchemaType.TERM, {'@id': value})


def _fetch_countries():
    return find_node(SchemaType.TERM, {
        'termType': TermTermType.REGION.value,
        'gadmLevel': 0
    }, SEARCH_LIMIT)


def _format_country_name(site: dict, as_id: bool = True):
    term = (site or {}).get('region') or (site or {}).get('country') or {}
    name = re.sub(r'[\(\)\,\.\'\"]', '', unidecode(term.get('name'))) if term.get('name') else None
    return name.lower().replace(' ', '-') if name and as_id else name


def _format_organic(organic: bool): return 'organic' if organic else 'conventional'


def _format_irrigated(irrigated: bool): return 'irrigated' if irrigated else 'non-irrigated'


def _is_global(country: dict): return country.get('@id', '').startswith('region-')


def should_aggregate(term: dict):
    lookup = download_lookup(f"{term.get('termType')}.csv", True)
    value = get_table_value(lookup, 'termid', term.get('@id'), column_name('skipAggregation'))
    return True if value is None or value == '' else not value


def linked_country(country: Union[str, dict]):
    return linked_node({
        **(get_by_name(country) if isinstance(country, str) else country),
        '@type': SchemaType.TERM.value
    })


def _term_lookup_dm(term: dict):
    lookup = download_lookup(f"{term.get('termType')}-lookup.csv")
    return safe_parse_float(get_table_value(lookup, 'termid', term.get('@id'), column_name(DRY_MATTER_TERM_ID)))


def _term_dm(term: dict):
    data = download_hestia(term.get('@id'))
    return safe_parse_float(find_term_match(data.get('defaultProperties', []), DRY_MATTER_TERM_ID).get('value'))


def term_dryMatter(term: dict): return _term_lookup_dm(term) or _term_dm(term)
