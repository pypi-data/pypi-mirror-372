# abstract_utilities/dynimport.py
from __future__ import annotations
import importlib, sys, os
from functools import lru_cache
from typing import Any, Callable, Iterable, Optional

class _LazyAttr:
    """Lazy resolver proxy to avoid import-time cycles.
    First use triggers actual import & attribute lookup.
    """
    __slots__ = ("_mod", "_attr", "_candidates", "_resolved")

    def __init__(self, module: str, attr: str, candidates: Iterable[str]):
        self._mod = module
        self._attr = attr
        self._candidates = candidates or None#tuple(candidates)
        self._resolved: Optional[Any] = None

    def _resolve(self) -> Any:
        if self._resolved is None:
            self._resolved = _resolve_attr(self._mod, self._attr, self._candidates)
        return self._resolved

    def __call__(self, *a, **k):
        return self._resolve()(*a, **k)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._resolve(), name)

    def __repr__(self) -> str:
        return f"<LazyAttr unresolved {self._mod}:{self._attr}>"

@lru_cache(maxsize=256)
def _resolve_attr(module: str, attr: str, candidates: Iterable[str]) -> Any:
    """Try module, then module + each candidate suffix for re-export patterns."""
    # 1) Try the module as-is
    candidates =candidates or tuple()
    mod = importlib.import_module(module)
    if hasattr(mod, attr):
        return getattr(mod, attr)

    # 2) Try dotted attribute lookup (e.g., attr="sub.mod:name" or "sub.name")
    if ":" in attr:
        left, right = attr.split(":", 1)
        submod = importlib.import_module(f"{module}.{left}")
        for part in right.split("."):
            submod = getattr(submod, part)
        return submod
    if "." in attr:
        obj = mod
        for part in attr.split("."):
            obj = getattr(obj, part)
        return obj

    # 3) Try common subpackages where APIs are often parked
    for suffix in candidates:
        try:
            sub = importlib.import_module(module + suffix)
        except Exception:
            continue
        if hasattr(sub, attr):
            return getattr(sub, attr)

    # 4) As a last resort, attempt an import that mimics "from pkg import name"
    #    by reloading after the import graph settles (helps with partial init).
    if module in sys.modules:
        try:
            mod = importlib.reload(sys.modules[module])
            if hasattr(mod, attr):
                return getattr(mod, attr)
        except Exception:
            pass

    raise ImportError(
        f"Could not resolve {attr!r} from {module!r}. "
        f"Tried direct, dotted, and suffixes: {list(candidates)}"
    )

def get_abstract_import(
    module: str,
    symbol: Optional[str] = None,
    *,
    lazy: bool = True,
    candidates: Iterable[str] = None,
    **kwargs: Any,
) -> Any:
    """Dynamic import helper that can return a lazy proxy to dodge cycles.

    Examples:
        get_abstract_import('abstract_gui', symbol='get_for_all_tabs')
        get_abstract_import(**{'module':'abstract_gui','import':'get_for_all_tabs'})
        get_abstract_import('abstract_gui', 'SIMPLEGUI:get_for_all_tabs')   # aliases
        get_abstract_import('abstract_gui', 'SIMPLEGUI.get_for_all_tabs')   # dotted
    """
    # Allow the exact call style the user wants: import='name'
    if symbol is None and 'import' in kwargs:
        symbol = kwargs['import']
    if not symbol:
        raise TypeError("get_abstract_import requires a 'symbol' (or pass import='...').")
    if lazy:
        return _LazyAttr(module, symbol, candidates)
    return _resolve_attr(module, symbol, candidates)
def get_caller_path():
    frame = inspect.stack()[1]
    return os.path.abspath(frame.filename)
def get_caller_dir():
    frame = inspect.stack()[1]
    abspath = os.path.abspath(frame.filename)
    return os.path.dirname(abspath)
def call_for_all_tabs():
    get_for_all_tabs=  get_abstract_import(
                        module='abstract_gui',
                        symbol='get_for_all_tabs')
    root = get_caller_dir()
    get_for_all_tabs(root)
