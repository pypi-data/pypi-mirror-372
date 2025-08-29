from hestia_earth.schema import SchemaType, ProductStatsDefinition
from hestia_earth.utils.model import linked_node

from . import _set_dict_single


def new_product(data: dict):
    node = {'@type': SchemaType.PRODUCT.value}
    term = data.get('term')
    node['term'] = linked_node(term)
    value = data.get('value')
    if value is not None:
        node['value'] = [value]
        node['statsDefinition'] = ProductStatsDefinition.CYCLES.value
        _set_dict_single(node, 'economicValueShare', data.get('economicValueShare'), strict=True)
    if data.get('primary'):
        node['primary'] = True

    _set_dict_single(node, 'properties', data.get('properties'), strict=True)
    _set_dict_single(node, 'distribution', data.get('distribution'), strict=True)

    return node
