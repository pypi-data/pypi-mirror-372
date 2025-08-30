from typing import Type, Dict, Any, Optional, List, Callable
from types import ModuleType
import importlib

__all__ = [
    "implementation_module_to_name",
    "name_to_implementation_module",
]

def implementation_module_to_name(module : ModuleType) -> str:
    """
    Convert a backend module to its simplified name.
    """
    full_name = module.__name__
    if not full_name.startswith("xbarray.implementations."):
        raise ValueError(f"Module {full_name} is not a valid xbarray backend module.")

    submodule_name = full_name[len("xbarray.implementations"):]
    if '.' in submodule_name:
        raise ValueError(f"Module {full_name} is not a valid xbarray backend module.")
    return submodule_name

def name_to_implementation_module(name: str) -> Type[ModuleType]:
    """
    Convert a simplified backend name to its module.
    """
    try:
        return importlib.import_module(f"xbarray.implementations.{name}")
    except ImportError as e:
        raise ImportError(f"Could not import backend module '{name}'.") from e
    