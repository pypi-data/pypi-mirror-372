"""utility functions for work with nested arrays"""
import numpy
from virtmat.language.utilities.typemap import typemap


def get_nested_array(arr):
    """normalize array of n-dimensional arrays to n+1 dimensional arrays"""
    assert isinstance(arr, numpy.ndarray)
    if all(isinstance(e, typemap['Quantity']) for e in arr):
        data = [e.magnitude.tolist() for e in arr]
        return typemap['Quantity'](numpy.array(data), next(iter(arr)).units)
    assert all(isinstance(e, numpy.ndarray) for e in arr)
    return numpy.array([e.tolist() for e in arr])
