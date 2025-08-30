from typing import Union, Optional, Tuple, Any
from ._typing import ARRAY_TYPE, DTYPE_TYPE, DEVICE_TYPE, RNG_TYPE
import numpy as np

__all__ = [
    "random_number_generator",
    "random_discrete_uniform",
    "random_uniform",
    "random_exponential",
    "random_normal",
    "random_geometric",
    "random_permutation"
]

def random_number_generator(
    seed : Optional[int] = None,
    *,
    device : Optional[DEVICE_TYPE] = None
) -> RNG_TYPE:
    return np.random.default_rng(seed)

def random_discrete_uniform(
    shape : Union[int, Tuple[int, ...]], 
    /,
    from_num : int, 
    to_num : int, 
    *,
    rng : RNG_TYPE, 
    dtype : Optional[DTYPE_TYPE] = None, 
    device : Optional[DEVICE_TYPE] = None
) -> Tuple[RNG_TYPE, ARRAY_TYPE]:
    t = rng.integers(int(from_num), int(to_num), size=shape)
    if dtype is not None:
        t = t.astype(dtype)
    return rng, t

def random_uniform(
    shape: Union[int, Tuple[int, ...]], 
    /,
    *,
    rng : RNG_TYPE, 
    low : float = 0.0, high : float = 1.0,
    dtype : Optional[DTYPE_TYPE] = None, 
    device : Optional[DEVICE_TYPE] = None
) -> Tuple[RNG_TYPE, ARRAY_TYPE]:
    t = rng.uniform(float(low), float(high), size=shape)
    if dtype is not None:
        t = t.astype(dtype)
    return rng, t

def random_exponential(
    shape: Union[int, Tuple[int, ...]], 
    /,
    *,
    rng : RNG_TYPE,  
    lambd : float = 1.0, 
    dtype : Optional[DTYPE_TYPE] = None, 
    device : Optional[DEVICE_TYPE] = None
) -> Tuple[RNG_TYPE, ARRAY_TYPE]:
    t = rng.exponential(1.0 / float(lambd), size=shape)
    if dtype is not None:
        t = t.astype(dtype)
    return rng, t

def random_normal(
    shape: Union[int, Tuple[int, ...]],
    /,
    *, 
    rng : RNG_TYPE,
    mean : float = 0.0, std : float = 1.0, 
    dtype : Optional[DTYPE_TYPE] = None, 
    device : Optional[Any] = None
) -> Tuple[RNG_TYPE, ARRAY_TYPE]:
    t = rng.normal(mean, std, size=shape)
    if dtype is not None:
        t = t.astype(dtype)
    return rng, t


def random_geometric(
    shape: Union[int, Tuple[int, ...]], 
    /,
    *,
    p: float, 
    rng: RNG_TYPE,
    dtype: Optional[DTYPE_TYPE] = None, 
    device: Optional[Any] = None
) -> Tuple[RNG_TYPE, ARRAY_TYPE]:
    t = rng.geometric(p, size=shape)
    if dtype is not None:
        t = t.astype(dtype)
    return rng, t

def random_permutation(
    n : int,
    /,
    *,
    rng: RNG_TYPE,
    dtype: Optional[DTYPE_TYPE] = None,
    device: Optional[DEVICE_TYPE] = None
) -> Tuple[RNG_TYPE, ARRAY_TYPE]:
    t = rng.permutation(n)
    if dtype is not None:
        t = t.astype(dtype)
    return rng, t