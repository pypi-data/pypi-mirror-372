from typing import Union, Any, Optional
import jax
import numpy as np

__all__ = [
    'ARRAY_TYPE',
    'DTYPE_TYPE',
    'DEVICE_TYPE',
    'RNG_TYPE',
]

ARRAY_TYPE = jax.Array
DTYPE_TYPE = np.dtype
DEVICE_TYPE = Union[jax.Device, jax.sharding.Sharding]
RNG_TYPE = jax.Array
