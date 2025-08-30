from typing import Protocol, TypeVar, Optional, Any, Tuple, Union, Type
from typing_extensions import deprecated
from array_api_typing.typing_2024_12._array_typing import SetIndex, GetIndex, Array as ArrayAPI202412Array, Device, DType, PyCapsule, SupportsDLPack

__all__ = [
    "SetIndex",
    "GetIndex",
    "Array",
    "PyCapsule",
    "SupportsDLPack",
    "DType",
    "Device",
]

class Array(ArrayAPI202412Array, Protocol):
    @property
    @deprecated(
        "Some array libraries either do not have the device attribute or include it with an incompatible API. Use array_api_namespace.device() instead.",
    )
    def device(self) -> Device:
        pass
    
    @deprecated(
        "some array libraries do not have the `to_device` method. Use array_api_namespace.to_device() instead.",
    )
    def to_device(
        self, device: Device, /, *, stream: Optional[Union[int, Any]] = None
    ):
        pass
    
    @property
    @deprecated(
        "PyTorch defines size in an incompatible way. It also fixes dask.arrays behaviour which returns nan for unknown sizes, whereas the standard requires None.",
    )
    def size(self) -> Optional[int]:
        pass