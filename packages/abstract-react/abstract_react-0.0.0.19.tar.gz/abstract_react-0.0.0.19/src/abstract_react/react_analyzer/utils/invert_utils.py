from ..imports import *
from .graph_utils import *
from .utils import *
def invert_to_symbol_map(graph: dict, include_kinds: Optional[Set[str]] = None) -> dict:
    """
    Generic {symbolName: {'exported_in': [...], 'imported_in': [...]}}
    restricted to given export kinds if include_kinds is provided.
    """
    include_kinds = set(include_kinds or [])

    # Index of name -> kinds seen among exports
    name_kinds: Dict[str, Set[str]] = {}
    for f, data in graph['nodes'].items():
        kinds = data.get('kinds', {})
        for name, k in kinds.items():
            name_kinds.setdefault(name, set()).add(k)

    out: Dict[str, Dict[str, Set[str]]] = {}

    # Export side
    for f, data in graph['nodes'].items():
        kinds = data.get('kinds', {})
        for name, k in kinds.items():
            if include_kinds and k not in include_kinds:
                continue
            out.setdefault(name, {'exported_in': set(), 'imported_in': set()})
            out[name]['exported_in'].add(f)

    # Import side (edges carry 'named', but not kind; we map if the name is known to be of a requested kind somewhere)
    for e in graph['edges']:
        for n in (e.get('named') or []):
            if n in ('*', '<side-effect>'):
                continue
            if include_kinds:
                # add only if name is known exported as one of include_kinds
                if not (name_kinds.get(n, set()) & include_kinds):
                    continue
            out.setdefault(n, {'exported_in': set(), 'imported_in': set()})
            out[n]['imported_in'].add(e['from'])

    # to lists
    return {k: {'exported_in': sorted(v['exported_in']),
                'imported_in': sorted(v['imported_in'])}
            for k, v in out.items()}

def invert_to_function_map(graph: dict) -> dict:
    # treat only functions (optionally add 'class' if you want)
    return invert_to_symbol_map(graph, include_kinds={'function'})

def invert_to_variable_map(graph: dict) -> dict:
    # treat variables (const/let/var)
    return invert_to_symbol_map(graph, include_kinds={'const','let','var'})
