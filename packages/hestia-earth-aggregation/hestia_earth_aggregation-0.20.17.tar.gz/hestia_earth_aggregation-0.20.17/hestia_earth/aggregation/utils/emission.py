from hestia_earth.schema import EmissionMethodTier, SchemaType, EmissionStatsDefinition, TermTermType
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.lookup_utils import is_in_system_boundary

from . import _unique_nodes, _set_dict_single
from .term import METHOD_MODEL

_DEFAULT_TIER = EmissionMethodTier.TIER_1.value
_SKIP_BACKGROUND_EMISSIONS = [TermTermType.PROCESSEDFOOD.value]


def _include_emission(emission: dict, product: dict):
    return any([
        emission.get('methodTier') != EmissionMethodTier.BACKGROUND.value,
        product.get('termType') not in _SKIP_BACKGROUND_EMISSIONS
    ])


def new_emission(product: dict):
    def emission(data: dict):
        term = data.get('term', {})
        # only add emissions included in the System Boundary
        if is_in_system_boundary(term.get('@id')):
            node = {'@type': SchemaType.EMISSION.value}
            node['term'] = linked_node(term)
            value = data.get('value')
            if value is not None:
                node['value'] = [value]
                node['statsDefinition'] = EmissionStatsDefinition.CYCLES.value

            node['methodModel'] = METHOD_MODEL
            _set_dict_single(node, 'methodTier', data.get('methodTier'))
            inputs = data.get('inputs', [])
            # compute list of unique inputs, required for `background` emissions
            if inputs:
                _set_dict_single(node, 'inputs', list(map(linked_node, _unique_nodes(inputs))), strict=True)

            if data.get('methodTier') != EmissionMethodTier.NOT_RELEVANT.value:
                _set_dict_single(node, 'distribution', data.get('distribution'), strict=True)

            return node if _include_emission(node, product) else None
    return emission


def get_method_tier(emissions: list):
    values = set([e.get('methodTier', _DEFAULT_TIER) for e in emissions])
    return list(values)[0] if len(values) == 1 else _DEFAULT_TIER
