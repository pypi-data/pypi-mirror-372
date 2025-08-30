from typing import Union, Any, Optional
import numpy as np

__all__ = [
    'ARRAY_TYPE',
    'DTYPE_TYPE',
    'DEVICE_TYPE',
    'RNG_TYPE',
]

ARRAY_TYPE = np.ndarray
DTYPE_TYPE = np.dtype
DEVICE_TYPE = Any
RNG_TYPE = np.random.Generator
