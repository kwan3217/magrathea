"""
Describe purpose of this script here

Created: 9/22/25
"""

import numpy as np


def rebin_2d(arr, new_shape, func=np.mean):
    """
    Rebin the input two-dimensional array into a different shape.

    :param arr: numpy.ndarray, required
        Input array
    :param new_shape: tuple, required
        Desired shape. May be smaller or larger than the original array, but must be
        whole-number divisor or multiple of input arr shape.
    :param func: function, optional
        Optional function to be applied to elements of each bin in order to calculate
        the resulting bin value. This function must take two arguments: func(a, axis).
        Default is `numpy.mean`. This function is only used if the image is scaled down.

    :return: np.ndarray, binned image

    :Note: All currently-imagined use-cases resize the array to the same aspect ratio,
    IE the scaling factor is the same in both dimensions. The code doesn't check for
    this but *should* work for uneven scaling as long as both dimensions are integer
    divisors or multiples of the original and it scales both dimensions up or both
    down. It will *not* work and will raise an exception if the image is to be scaled
    up in one dimension and down in the other.

    If the image is to be scaled up, the func argument is ignored. Each pixel in the
    original image will get copied multiple times to cover an entire region in the
    new image.
    """
    if new_shape == arr.shape:
        return arr.copy()
    elif new_shape[0] < arr.shape[0]:
        if new_shape[1] > arr.shape[1]:
            raise ValueError("Scaled down in first dimension and up in second")
        # Inspired by: https://scipython.com/blog/binning-a-2d-array-in-numpy/
        # Works by reshaping the 2D input array into a 4D array where bins lineup along
        # axis 1 and 3. Then the input `func` function is applied along those axes to achieve
        # binning.
        if arr.shape[0] % new_shape[0] != 0 or arr.shape[1] % new_shape[1] != 0:
            raise ValueError("Not a whole number scale factor")
        shape = (new_shape[0], arr.shape[0] // new_shape[0],
                 new_shape[1], arr.shape[1] // new_shape[1])
        return np.squeeze(np.apply_over_axes(func, arr.reshape(shape), (-1, 1)), (-1, 1))
    else:
        if new_shape[1] < arr.shape[1]:
            raise ValueError("Scaled up in first dimension and down in second")
        result=np.zeros(new_shape)
        if new_shape[0] % arr.shape[0] != 0 or new_shape[1] % arr.shape[1] != 0:
            raise ValueError("Not a whole number scale factor")
        yr=new_shape[0] // arr.shape[0]
        xr=new_shape[1] // arr.shape[1]
        for j in range(yr):
            for i in range(xr):
                result[j::yr, i::xr] = arr
        return result


def rebin_rgb(arr, new_shape, func=np.mean):
    if new_shape == arr.shape:
        return arr.copy()
    elif new_shape[0] < arr.shape[0]:
        if new_shape[1] > arr.shape[1]:
            raise ValueError("Scaled down in first dimension and up in second")
        # Inspired by: https://scipython.com/blog/binning-a-2d-array-in-numpy/
        # Works by reshaping the 2D input array into a 4D array where bins lineup along
        # axis 1 and 3. Then the input `func` function is applied along those axes to achieve
        # binning.
        if arr.shape[0] % new_shape[0] != 0 or arr.shape[1] % new_shape[1] != 0:
            raise ValueError("Not a whole number scale factor")
        shape = (new_shape[0], arr.shape[0] // new_shape[0],
                 new_shape[1], arr.shape[1] // new_shape[1])+new_shape[2:]
        return np.squeeze(np.apply_over_axes(func, arr.reshape(shape), (3, 1)), (3, 1))
    else:
        raise NotImplementedError("Expansion of RGB not yet implemented")
        if new_shape[1] < arr.shape[1]:
            raise ValueError("Scaled up in first dimension and down in second")
        result=np.zeros(new_shape)
        if new_shape[0] % arr.shape[0] != 0 or new_shape[1] % arr.shape[1] != 0:
            raise ValueError("Not a whole number scale factor")
        yr=new_shape[0] // arr.shape[0]
        xr=new_shape[1] // arr.shape[1]
        for j in range(yr):
            for i in range(xr):
                result[j::yr, i::xr] = arr
        return result
