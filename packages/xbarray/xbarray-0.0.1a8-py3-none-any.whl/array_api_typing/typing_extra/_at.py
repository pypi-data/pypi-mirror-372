from typing import Protocol, TypeVar, Optional, Any, Tuple, Union, Type, TypedDict, List
from abc import abstractmethod
from array_api_typing.typing_compat._api_typing import _NAMESPACE_ARRAY
from array_api_typing.typing_compat._array_typing import SetIndex

class AtResult(Protocol[_NAMESPACE_ARRAY]):
    @abstractmethod
    def __getitem__(self, idx: SetIndex, /) -> "AtResult[_NAMESPACE_ARRAY]":
        """
        Allow for the alternate syntax ``at(x)[start:stop:step]``.

        It looks prettier than ``at(x, slice(start, stop, step))``
        and feels more intuitive coming from the JAX documentation.
        """
        pass

    @abstractmethod
    def set(
        self,
        y: Union[_NAMESPACE_ARRAY, float, int, complex],
        /,
        copy: Optional[bool] = None,
    ) -> _NAMESPACE_ARRAY:
        pass

    @abstractmethod
    def add(
        self,
        y: Union[_NAMESPACE_ARRAY, float, int, complex],
        /,
        copy: Optional[bool] = None,
    ) -> _NAMESPACE_ARRAY:
        pass

    @abstractmethod
    def subtract(
        self,
        y: Union[_NAMESPACE_ARRAY, float, int, complex],
        /,
        copy: Optional[bool] = None,
    ) -> _NAMESPACE_ARRAY:
        pass

    @abstractmethod
    def multiply(
        self,
        y: Union[_NAMESPACE_ARRAY, float, int, complex],
        /,
        copy: Optional[bool] = None,
    ) -> _NAMESPACE_ARRAY:
        pass

    @abstractmethod
    def divide(
        self,
        y: Union[_NAMESPACE_ARRAY, float, int, complex],
        /,
        copy: Optional[bool] = None,
    ) -> _NAMESPACE_ARRAY:
        pass

    @abstractmethod
    def power(
        self,
        y: Union[_NAMESPACE_ARRAY, float, int, complex],
        /,
        copy: Optional[bool] = None,
    ) -> _NAMESPACE_ARRAY:
        pass

    @abstractmethod
    def min(
        self,
        y: Union[_NAMESPACE_ARRAY, float, int, complex],
        /,
        copy: Optional[bool] = None,
    ) -> _NAMESPACE_ARRAY:
        pass
    
    @abstractmethod
    def max(
        self,
        y: Union[_NAMESPACE_ARRAY, float, int, complex],
        /,
        copy: Optional[bool] = None,
    ) -> _NAMESPACE_ARRAY:
        pass