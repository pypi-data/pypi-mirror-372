"""apply various constraints for literal values"""
from virtmat.language.utilities.errors import textxerror_wrap, StaticValueError


@textxerror_wrap
def check_resources_values(obj):
    """object processor to check Resources objects for general validity"""
    if obj.ncores is not None and obj.ncores < 1:
        raise StaticValueError('number of cores must be a positive integer number')
    if obj.walltime is not None and obj.walltime.value <= 0:
        raise StaticValueError('walltime must be a positive number')
    if obj.memory is not None and obj.memory.value <= 0:
        raise StaticValueError('memory must be a positive number')


@textxerror_wrap
def check_number_of_chunks(obj):
    """check number of chunks in parallelizable objects"""
    if obj.nchunks is not None and obj.nchunks < 1:
        raise StaticValueError('number of chunks must be a positive integer number')
