from typing import Any, Union, Callable
from array_api_typing.typing_compat import ArrayAPINamespace as CompatNamespace, ArrayAPIArray as CompatArray, ArrayAPIDType as CompatDType
import array_api_compat

__all__ = [
    "get_abbreviate_array_function",
    "get_map_fn_over_arrays_function",
]

def get_abbreviate_array_function(
    backend : CompatNamespace[CompatArray, Any, Any],
    default_integer_dtype : CompatDType,
    func_dtype_is_real_floating : Callable[[CompatDType], bool],
    func_dtype_is_real_integer : Callable[[CompatDType], bool],
    func_dtype_is_boolean : Callable[[CompatDType], bool],
):
    def abbreviate_array(array : CompatArray, try_cast_scalar : bool = True) -> Union[float, int, CompatArray]:
        """
        Abbreivates an array to a single element if possible.
        Or, if some dimensions are the same, abbreviates to a smaller array (but with the same number of dimensions).
        """
        abbr_array = array
        idx = backend.zeros(1, dtype=default_integer_dtype, device=array_api_compat.device(abbr_array))
        for dim_i in range(len(array.shape)):
            first_elem = backend.take(abbr_array, idx, axis=dim_i)
            if backend.all(abbr_array == first_elem):
                abbr_array = first_elem
            else:
                continue
        if try_cast_scalar:
            if all(i == 1 for i in abbr_array.shape):
                elem = abbr_array[tuple([0] * len(abbr_array.shape))]
                if func_dtype_is_real_floating(elem.dtype):
                    return float(elem)
                elif func_dtype_is_real_integer(elem.dtype):
                    return int(elem)
                elif func_dtype_is_boolean(elem.dtype):
                    return bool(elem)
                else:
                    raise ValueError(f"Abbreviated array element dtype must be a real floating or integer or boolean type, actual dtype: {elem.dtype}")
        else:
            return array
    return abbreviate_array

def get_map_fn_over_arrays_function(
    is_backendarray : Callable[[Any], bool],
):
    def map_fn_over_arrays(data : Any, func : Callable[[CompatArray], CompatArray]) -> Any:
        """
        Map a function to the data.
        """
        if is_backendarray(data):
            return func(data)
        elif isinstance(data, dict):
            return {k: map_fn_over_arrays(v, func) for k, v in data.items()}
        elif isinstance(data, tuple):
            return tuple(map_fn_over_arrays(i, func) for i in data)
        elif isinstance(data, list):
            return [map_fn_over_arrays(i, func) for i in data]
        else:
            return data
    return map_fn_over_arrays
