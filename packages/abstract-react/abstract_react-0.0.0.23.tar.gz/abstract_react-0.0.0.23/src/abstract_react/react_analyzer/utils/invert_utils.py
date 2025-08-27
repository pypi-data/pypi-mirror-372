from ..imports import *
from .graph_utils import *
from .utils import *
# react_analyzer/utils/invert_utils.py
def invert_to_symbol_map(graph: dict, include_kinds: Optional[Set[str]] = None) -> dict:
    include_kinds = set(include_kinds or [])

    # Build export-kind index per module
    module_kinds: Dict[str, Dict[str, str]] = {
        mod: (data.get('kinds') or {}) for mod, data in graph.get('nodes', {}).items()
    }

    out: Dict[str, Dict[str, Set[str]]] = {}

    # Export side
    for mod, data in graph.get('nodes', {}).items():
        kinds = data.get('kinds', {})  # {name: kind}
        for name, k in kinds.items():
            if include_kinds and k not in include_kinds:
                continue
            out.setdefault(name, {'exported_in': set(), 'imported_in': set()})
            out[name]['exported_in'].add(mod)

    # Import side: keep only names whose DEST module exports them with a matching kind
    for e in graph.get('edges', []):
        dst = e.get('to')  # module path we import from
        dst_kinds = module_kinds.get(dst, {})
        for n in (e.get('named') or []):
            if n in ('*', '<side-effect>', '<default>'):
                continue
            if include_kinds:
                k = dst_kinds.get(n)
                if k not in include_kinds:
                    continue
            out.setdefault(n, {'exported_in': set(), 'imported_in': set()})
            out[n]['imported_in'].add(e['from'])

    # to lists
    return {
        k: {'exported_in': sorted(v['exported_in']),
            'imported_in': sorted(v['imported_in'])}
        for k, v in out.items()
    }

def invert_to_function_map(graph: dict) -> dict:
    # treat only functions (optionally add 'class' if you want)
    return invert_to_symbol_map(graph, include_kinds={'function'})

def invert_to_variable_map(graph: dict) -> dict:
    # treat variables (const/let/var)
    return invert_to_symbol_map(graph, include_kinds={'const','let','var'})
