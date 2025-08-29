'''
Module with utility functions to handle numpy arrays
'''

import math
import numpy

#-----------------------------------------------
def _check_ftimes(ftimes : float) -> None:
    '''
    Check if floating scale factor makes sense
    '''
    if not isinstance(ftimes, float):
        raise TypeError(f'Scaling factor is not a float, but: {ftimes}')

    if ftimes <= 1.0:
        raise ValueError(f'Scaling factor needs to be larger than 1.0, found: {ftimes}')
#-----------------------------------------------
def repeat_arr(arr_val : numpy.ndarray, ftimes : float) -> numpy.ndarray:
    '''
    Will repeat elements in an array a non integer number of times.

    arr_val: 1D array of objects
    ftimes (float): Number of times to repeat it.
    '''

    _check_ftimes(ftimes)

    a = math.floor(ftimes)
    b = math.ceil(ftimes)
    if numpy.isclose(a, b):
        return numpy.repeat(arr_val, a)

    # Will split randomly data in arr_val, such that one set will get increased
    # by floor(ftimes) and the other by ceiling(ftimes)

    # Get probability that given element belongs to dataset weighted by "a"
    p         = b - ftimes
    size_t    = len(arr_val)
    size_1    = int(p * size_t)

    # Find subset to weight by "a"
    arr_ind_1 = numpy.random.choice(size_t, size=size_1, replace=False)
    arr_val_1 = arr_val[arr_ind_1]

    # Find subset to weight by "b"
    arr_ind_2 = numpy.setdiff1d(numpy.arange(size_t), arr_ind_1)
    arr_val_2 = arr_val[arr_ind_2]

    # Repeat them an integer number of times
    arr_val_1 = numpy.repeat(arr_val_1, a)
    arr_val_2 = numpy.repeat(arr_val_2, b)

    return numpy.concatenate([arr_val_1, arr_val_2])
#-----------------------------------------------
