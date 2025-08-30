"""deepcopy implementation for metamodel classes"""
from copy import deepcopy
from textx import get_metamodel, textx_isinstance


def is_general_variable(var, meta):
    """return true if var is a GeneralVariable instance"""
    classes = [meta['Variable'], meta['Dummy'], meta['ObjectImport']]
    return any(textx_isinstance(var, cls) for cls in classes)


def __deepcopy__(self, memo):
    cls = self.__class__
    result = cls.__new__(cls)
    memo[id(self)] = result
    meta = get_metamodel(self)
    for key, val in self.__dict__.items():
        if key == 'parent':
            # must stay a reference
            result.parent = self.parent
        elif key == 'function':
            result.function = self.function
        elif key == 'args':
            result.args = self.args
        elif key == 'ref' and is_general_variable(self.ref, meta):
            result.ref = self.ref
        else:
            # must be copied
            setattr(result, key, deepcopy(val, memo))
    self.last_copy = result
    return result


def add_deepcopy(metamodel):
    """Add deepcopy method to metamodel classes using monkey style patching"""
    metamodel['IfFunction'].__deepcopy__ = __deepcopy__
    metamodel['IfExpression'].__deepcopy__ = __deepcopy__
    metamodel['FunctionCall'].__deepcopy__ = __deepcopy__
    metamodel['Real'].__deepcopy__ = __deepcopy__
    metamodel['Imag'].__deepcopy__ = __deepcopy__
    metamodel['Variable'].__deepcopy__ = __deepcopy__
    metamodel['Dummy'].__deepcopy__ = __deepcopy__
    metamodel['GeneralReference'].__deepcopy__ = __deepcopy__
    metamodel['IterableProperty'].__deepcopy__ = __deepcopy__
    metamodel['IterableQuery'].__deepcopy__ = __deepcopy__
    metamodel['ObjectAccessor'].__deepcopy__ = __deepcopy__
    metamodel['Factor'].__deepcopy__ = __deepcopy__
    metamodel['Power'].__deepcopy__ = __deepcopy__
    metamodel['Term'].__deepcopy__ = __deepcopy__
    metamodel['Expression'].__deepcopy__ = __deepcopy__
    metamodel['Operand'].__deepcopy__ = __deepcopy__
    metamodel['BooleanOperand'].__deepcopy__ = __deepcopy__
    metamodel['And'].__deepcopy__ = __deepcopy__
    metamodel['Or'].__deepcopy__ = __deepcopy__
    metamodel['Not'].__deepcopy__ = __deepcopy__
    metamodel['Comparison'].__deepcopy__ = __deepcopy__
    metamodel['Tuple'].__deepcopy__ = __deepcopy__
    metamodel['Dict'].__deepcopy__ = __deepcopy__
    metamodel['Quantity'].__deepcopy__ = __deepcopy__
    metamodel['Number'].__deepcopy__ = __deepcopy__
    metamodel['Bool'].__deepcopy__ = __deepcopy__
    metamodel['String'].__deepcopy__ = __deepcopy__
    metamodel['Lambda'].__deepcopy__ = __deepcopy__
    metamodel['Map'].__deepcopy__ = __deepcopy__
    metamodel['Filter'].__deepcopy__ = __deepcopy__
    metamodel['Reduce'].__deepcopy__ = __deepcopy__
    metamodel['Sum'].__deepcopy__ = __deepcopy__
    metamodel['Any'].__deepcopy__ = __deepcopy__
    metamodel['All'].__deepcopy__ = __deepcopy__
    metamodel['In'].__deepcopy__ = __deepcopy__
    metamodel['Range'].__deepcopy__ = __deepcopy__
