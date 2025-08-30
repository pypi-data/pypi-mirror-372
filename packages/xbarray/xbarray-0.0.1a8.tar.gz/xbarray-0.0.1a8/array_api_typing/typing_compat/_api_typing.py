from typing import Protocol, TypeVar, Optional, Any, Tuple, Union, Type
from typing_extensions import deprecated
from abc import abstractmethod
from array_api_typing.typing_2024_12._api_typing import ArrayAPINamespace as ArrayAPI202412Namespace, _NAMESPACE_C, _NAMESPACE_ARRAY, _NAMESPACE_DEVICE, _NAMESPACE_DTYPE

class ArrayAPINamespace(ArrayAPI202412Namespace[_NAMESPACE_ARRAY, _NAMESPACE_DEVICE, _NAMESPACE_DTYPE], Protocol[_NAMESPACE_ARRAY, _NAMESPACE_DEVICE, _NAMESPACE_DTYPE]):
    @abstractmethod
    def device(self, x : _NAMESPACE_ARRAY, /) -> _NAMESPACE_DEVICE:
        pass

    @abstractmethod
    def to_device(
        self,
        x: _NAMESPACE_ARRAY,
        device: _NAMESPACE_DEVICE,
        /,
        *,
        stream : Optional[Union[int, Any]] = None,
    ) -> _NAMESPACE_ARRAY:
        pass

    @abstractmethod
    def size(
        self,
        x: _NAMESPACE_ARRAY
    ) -> Optional[int]:
        pass