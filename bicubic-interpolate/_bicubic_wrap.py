import numpy as np

from ._bicubic import interpolate as _interpolate

def interpolate(data: np.ndarray, shape, a=-.75):
    d = data.astype(float)
    return _interpolate(d, shape[0], shape[1], a)
