"""input/output processors"""
from textx import get_children_of_type
from virtmat.language.utilities.errors import textxerror_wrap
from virtmat.language.utilities.serializable import FWDataObject


@textxerror_wrap
def object_to(obj):
    """Store an object to file or url"""
    data_obj = FWDataObject.from_obj(obj.ref.parameter.value)
    datastore = {'type': 'file'} if obj.filename else {'type': 'url'}
    data_obj.offload_data(datastore=datastore, url=obj.url, filename=obj.filename)


def output_processor(model, _):
    """store objects to files or urls"""
    for obj in get_children_of_type('ObjectTo', model):
        object_to(obj)
