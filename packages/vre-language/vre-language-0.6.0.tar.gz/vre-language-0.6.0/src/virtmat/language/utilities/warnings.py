"""handling domain-specific warnings"""
import warnings
from virtmat.language.utilities.textx import get_location_context
from virtmat.language.utilities.errors import format_textxerr_msg


class TextSUserWarning(UserWarning):
    """warning to use within the processors"""
    def __init__(self, *args, obj=None, **kwargs):
        self.obj = obj
        super().__init__(*args, **kwargs)
        if obj:
            for key, val in get_location_context(obj).items():
                setattr(self, key, val)
            self.message = str(self)


def format_warning_wrapper(func):
    """format domain-specific warnings; leave python warnings unchanged"""
    def wrapper(*args, **kwargs):
        warning = args[0]
        warning_cls = args[1]
        if isinstance(warning, TextSUserWarning):
            assert warning_cls is TextSUserWarning
            if warning.obj:
                return 'Warning: ' + format_textxerr_msg(warning) + '\n'
            return 'Warning: ' + str(warning) + '\n'
        return func(*args, **kwargs)
    return wrapper


warnings.formatwarning = format_warning_wrapper(warnings.formatwarning)
