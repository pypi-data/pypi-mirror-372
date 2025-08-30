from xbarray.cls_impl.cls_base import ComputeBackendImplCls
from ._src.implementations import pytorch as pytorch_impl

class PytorchComputeBackend(metaclass=ComputeBackendImplCls):
    ARRAY_TYPE = pytorch_impl.ARRAY_TYPE
    DTYPE_TYPE = pytorch_impl.DTYPE_TYPE
    DEVICE_TYPE = pytorch_impl.DEVICE_TYPE
    RNG_TYPE = pytorch_impl.RNG_TYPE

for name in dir(pytorch_impl):
    if not name.startswith('_') or name in [
        '__array_namespace_info__',
        '__array_api_version__',
    ]:
        setattr(PytorchComputeBackend, name, getattr(pytorch_impl, name))

__all__ = [
    'PytorchComputeBackend',
]