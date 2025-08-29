from hestia_earth.utils.model import linked_node
from hestia_earth.utils.tools import non_empty_list, flatten


def format_aggregated_sources(nodes: list, node_key: str = 'source'):
    sources = non_empty_list(flatten([n.get('aggregatedSources', n.get(node_key)) for n in nodes]))
    sources = non_empty_list([
        v if v is None else v if isinstance(v, dict) else {
            '@type': 'Source',
            '@id': v
        } for v in sources
    ])
    return sorted(
        list(map(linked_node, [dict(t) for t in {tuple(d.items()) for d in sources}])),
        key=lambda x: x.get('@id')
    )
