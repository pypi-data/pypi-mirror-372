from types import ModuleType
from typing import Type
from xbarray._src.serialization import implementation_module_to_name, name_to_implementation_module

class ComputeBackendImplCls(Type):
    def __str__(self):
        return self.simplified_name
    
    def __repr__(self):
        return self.simplified_name