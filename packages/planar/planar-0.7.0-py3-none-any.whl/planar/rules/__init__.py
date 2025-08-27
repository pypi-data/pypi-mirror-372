import importlib
from typing import Any

_DEFERRED_IMPORTS = {
    "rule": ".decorator",
    "Rule": ".models",
    "RuleSerializeable": ".models",
}


def __getattr__(name: str) -> Any:
    """
    Lazily import modules to avoid circular dependencies.
    This is called by the Python interpreter when a module attribute is accessed
    that cannot be found in the module's __dict__.
    PEP 562
    """
    if name in _DEFERRED_IMPORTS:
        module_path = _DEFERRED_IMPORTS[name]
        module = importlib.import_module(module_path, __name__)
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
