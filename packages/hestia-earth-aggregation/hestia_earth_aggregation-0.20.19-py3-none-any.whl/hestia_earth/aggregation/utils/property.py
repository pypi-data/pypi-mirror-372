from functools import reduce
from hestia_earth.schema import SchemaType
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.tools import non_empty_list

from . import weighted_average
from .blank_node import group_by_term_id


def new_property(data: dict):
    node = {'@type': SchemaType.PROPERTY.value}
    term = data.get('term')
    node['term'] = linked_node(term)
    value = data.get('value')
    if value is not None:
        node['value'] = value
    return node


def aggregate_properties(properties: list):
    grouped_properties = reduce(group_by_term_id, properties, {})
    return [
        new_property({
            'term': values[0].get('term'),
            'value': weighted_average(non_empty_list([(v.get('value'), 1) for v in values]))
        })
        for values in grouped_properties.values()
    ]
