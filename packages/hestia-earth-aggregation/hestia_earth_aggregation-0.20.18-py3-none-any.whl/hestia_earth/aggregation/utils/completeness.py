from functools import reduce
from hestia_earth.schema import (
    SchemaType, TermTermType, CompletenessField, COMPLETENESS_MAPPING, CompletenessJSONLD, EmissionMethodTier
)
from hestia_earth.utils.tools import non_empty_list


_ANIMAL_FEED_INPUT_MAPPING = {
    SchemaType.INPUT.value: {
        TermTermType.ANIMALPRODUCT.value: CompletenessField.ANIMALFEED.value,
        TermTermType.CROP.value: CompletenessField.ANIMALFEED.value,
        TermTermType.PROCESSEDFOOD.value: CompletenessField.ANIMALFEED.value,
    }
}
_TERM_TYPE_COMPLETENESS_MAPPING = {
    TermTermType.ANIMALPRODUCT.value: _ANIMAL_FEED_INPUT_MAPPING,
    TermTermType.LIVEANIMAL.value: _ANIMAL_FEED_INPUT_MAPPING,
    TermTermType.LIVEAQUATICSPECIES.value: _ANIMAL_FEED_INPUT_MAPPING,
}
_DEFAULT_COMPLETENESS_MAPPING = {
    SchemaType.MANAGEMENT.value: {
        TermTermType.CROPRESIDUEMANAGEMENT.value: CompletenessField.CROPRESIDUE.value
    }
}
_MULTI_COMPLETENESS_JOIN = '-'


def emission_completeness_key(emission: dict):
    return _MULTI_COMPLETENESS_JOIN.join(
        sorted(set(non_empty_list([
            COMPLETENESS_MAPPING.get('Input').get(i.get('termType'))
            for i in emission.get('inputs', [])
        ])))
    ) if emission.get('methodTier') == EmissionMethodTier.BACKGROUND.value else None


_SCHEMA_TYPE_COMPLETENESS_KEY = {
    SchemaType.EMISSION.value: emission_completeness_key
}


def blank_node_completeness_key(blank_node: dict, product: dict = None):
    term_type = blank_node.get('term', {}).get('termType')
    node_type = blank_node.get('@type') or blank_node.get('type')
    product_term_type = ((product or {}).get('term') or product or {}).get('termType')
    mapping = (
        (_TERM_TYPE_COMPLETENESS_MAPPING.get(product_term_type, {}).get(node_type) if product else {}) or
        COMPLETENESS_MAPPING.get(node_type) or
        _DEFAULT_COMPLETENESS_MAPPING.get(node_type)
    )
    return (
        (mapping or {}).get(term_type) or
        _SCHEMA_TYPE_COMPLETENESS_KEY.get(node_type, lambda *args: None)(blank_node)
    )


def is_complete(node: dict, product: dict, blank_node: dict):
    completeness_key = blank_node_completeness_key(blank_node, product=product)
    # key can be compose of multiple keys, in which case all must be complete
    keys = completeness_key.split(_MULTI_COMPLETENESS_JOIN) if completeness_key else []
    return all([
        node.get('completeness', {}).get(key, False) for key in keys
    ]) if keys else None


def completeness_count(completeness: dict, completeness_key: str = None):
    # key can be composed of multiple keys, in which case we use the one with the highest found count
    keys = completeness_key.split(_MULTI_COMPLETENESS_JOIN) if completeness_key else []
    return max(non_empty_list([completeness.get(key, 0) for key in keys])) if keys else 0


def completeness_from_count(completeness_count: dict):
    completeness = CompletenessJSONLD().to_dict()
    keys = list(completeness.keys())
    keys.remove('@type')
    return completeness | {key: completeness_count.get(key, 0) > 0 for key in keys}


def aggregate_completeness(values: list):
    def is_complete(key: str):
        return any([v.get('completeness', v).get(key) is True for v in values])

    completeness = CompletenessJSONLD().to_dict()
    keys = list(completeness.keys())
    keys.remove('@type')
    return completeness | reduce(lambda prev, curr: prev | {curr: is_complete(curr)}, keys, {})


def combine_completeness_count(values: list[dict]) -> dict[str, int]:
    def count_completeness(key: str):
        return len([v for v in values if v.get(key)])

    completeness = CompletenessJSONLD().to_dict()
    keys = list(completeness.keys())
    keys.remove('@type')
    return {key: count_completeness(key) for key in keys}


def sum_completeness_count(values: list[dict]) -> dict[str, int]:
    def sum_completeness(key: str):
        return sum([v.get(key) for v in values])

    completeness = CompletenessJSONLD().to_dict()
    keys = list(completeness.keys())
    keys.remove('@type')
    return {key: sum_completeness(key) for key in keys}
