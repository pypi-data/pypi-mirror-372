from xbarray.cls_impl.cls_base import ComputeBackendImplCls
from ._src.implementations import numpy as numpy_impl

class NumpyComputeBackend(metaclass=ComputeBackendImplCls):
    ARRAY_TYPE = numpy_impl.ARRAY_TYPE
    DTYPE_TYPE = numpy_impl.DTYPE_TYPE
    DEVICE_TYPE = numpy_impl.DEVICE_TYPE
    RNG_TYPE = numpy_impl.RNG_TYPE

for name in dir(numpy_impl):
    if not name.startswith('_') or name in [
        '__array_namespace_info__',
        '__array_api_version__',
    ]:
        setattr(NumpyComputeBackend, name, getattr(numpy_impl, name))

__all__ = [
    'NumpyComputeBackend',
]