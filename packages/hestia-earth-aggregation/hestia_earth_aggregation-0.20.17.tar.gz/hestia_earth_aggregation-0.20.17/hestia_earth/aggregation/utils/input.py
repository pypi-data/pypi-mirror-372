from hestia_earth.schema import SchemaType, InputStatsDefinition
from hestia_earth.utils.model import linked_node

from . import _set_dict_single
from .blank_node import get_lookup_value


def new_input(product: dict, country: dict):
    # list of inputs matching the country
    input_term_ids = (get_lookup_value(product, 'aggregationInputTermIds') or '').split(';')

    def input(data: dict):
        node = {'@type': SchemaType.INPUT.value}
        term = data.get('term')
        node['term'] = linked_node(term)
        value = data.get('value')
        if value is not None:
            node['value'] = [value]
            node['statsDefinition'] = InputStatsDefinition.CYCLES.value
        _set_dict_single(node, 'properties', data.get('properties'), strict=True)
        if term.get('@id') in input_term_ids:
            node['country'] = linked_node(country)
        _set_dict_single(node, 'distribution', data.get('distribution'), strict=True)
        return node
    return input
