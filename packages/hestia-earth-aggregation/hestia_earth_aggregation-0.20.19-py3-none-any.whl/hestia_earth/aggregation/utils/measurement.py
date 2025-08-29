from hestia_earth.schema import MeasurementJSONLD, MeasurementStatsDefinition, MeasurementMethodClassification
from hestia_earth.utils.model import linked_node

from . import _set_dict_array, _set_dict_single


def new_measurement(data: dict):
    node = MeasurementJSONLD().to_dict()
    node['term'] = linked_node(data.get('term'))
    node['methodClassification'] = MeasurementMethodClassification.COUNTRY_LEVEL_STATISTICAL_DATA.value

    value = data.get('value')
    if value is not None:
        node['value'] = [value]
        node['statsDefinition'] = MeasurementStatsDefinition.SITES.value

    _set_dict_array(node, 'observations', data.get('observations'))
    _set_dict_array(node, 'min', data.get('min'))
    _set_dict_array(node, 'max', data.get('max'))
    _set_dict_array(node, 'sd', data.get('sd'), True)

    _set_dict_single(node, 'startDate', data.get('startDate'), strict=True)
    _set_dict_single(node, 'endDate', data.get('endDate'), strict=True)
    _set_dict_single(node, 'properties', data.get('properties'), strict=True)
    _set_dict_single(node, 'distribution', data.get('distribution'), strict=True)

    if data.get('depthUpper') is not None:
        node['depthUpper'] = int(data.get('depthUpper'))
    if data.get('depthLower') is not None:
        node['depthLower'] = int(data.get('depthLower'))

    return node
