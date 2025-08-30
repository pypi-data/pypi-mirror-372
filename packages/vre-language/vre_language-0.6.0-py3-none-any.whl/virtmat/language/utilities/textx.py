# pylint: disable=protected-access
"""Utility functions for textx"""
import re
import sys
import traceback
from os import path
from arpeggio import StrMatch, RegExMatch
from textx import metamodel_from_str
from textx import get_metamodel, get_model, get_location
from textx import get_children, get_parent_of_type
from textx import textx_isinstance
from textx.exceptions import TextXSyntaxError, TextXSemanticError
import virtmat
from virtmat.language.utilities.logging import get_logger

GRAMMAR_LOC = path.join(virtmat.language.__path__[0], 'grammar', 'virtmat.tx')


def isinstance_m(obj, classes):
    """
    Check whether an object is an instance of metamodel classes
    Args:
        obj: a model object
        classes: an iterable with names of classes from the metamodel
    Returns:
        True (False) if the object is (is not) instance of any class
    """
    meta = get_metamodel(obj)
    return any(textx_isinstance(obj, meta[c]) for c in classes)


def isinstance_r(obj, classes):
    """
    Check whether an instance of a class from classes is referenced in obj
    Args:
        obj: a model object
        classes: an iterable with names of classes from the metamodel
    Returns:
        True if an instance of the class is referenced, otherwise False
    """
    if hasattr(obj, 'ref'):
        ret = isinstance_r(obj.ref, classes)
    elif isinstance_m(obj, ['Variable']):
        ret = isinstance_r(obj.parameter, classes)
    else:
        ret = isinstance_m(obj, classes)
    return ret


def is_reference(obj, metamodel):
    """return True if obj is a GeneralReference"""
    return textx_isinstance(obj, metamodel['GeneralReference'])


def get_reference(obj):
    """return the referenced object if obj is a reference and obj otherwise"""
    metamodel = get_metamodel(obj)
    if is_reference(obj, metamodel):
        if textx_isinstance(obj.ref, metamodel['Variable']):
            return obj.ref.parameter
        return obj.ref
    return obj


def get_context(obj):
    """get the source code section pertinent to a textx model object obj"""
    src = getattr(get_model(obj), '_tx_model_params').get('source_code')
    beg = getattr(obj, '_tx_position')
    end = getattr(obj, '_tx_position_end')
    return None if src is None else src[beg:end].rstrip()


def get_location_context(obj):
    """get location and source code of a textx model object"""
    return {**get_location(obj), 'context': get_context(obj)}


def where_used(obj):
    """get a parent object where the object has been used"""
    stats = (('FunctionCall', 'params'), ('Variable', 'parameter'),
             ('PrintParameter', 'param'))
    parents = ((get_parent_of_type(s, obj), p) for s, p in stats)
    parent, param = next((p, par) for p, par in parents if p is not None)
    if isinstance_m(parent, ['FunctionCall']):
        params = [p for p in parent.params if get_children(lambda x: x is obj, p)]
        if params:
            assert len(params) == 1
            return next(iter(params))
        return next(iter(parent.params))
    return getattr(parent, param)


def get_object_str(src, obj):
    """extract the source string of a textx object from the model string"""
    return src[obj._tx_position:obj._tx_position_end].strip()


def get_identifiers(obj):
    """return a list of identifier objects"""
    classes = ['Variable', 'FunctionDefinition', 'ObjectImport']
    return get_children(lambda x: isinstance_m(x, classes), obj)


class GrammarString:
    """create a single textX grammar string from a modular textX grammar"""
    __regex = r'^import\s+(\S+)$'

    def __init__(self, grammar_path=GRAMMAR_LOC):
        self.grammar_dir = path.dirname(grammar_path)
        self.__memo = set()
        self.__string = ''.join(self._expand_grammar(grammar_path))

    @property
    def string(self):
        """string getter"""
        return self.__string

    def _expand_grammar(self, filename):
        """recursively expand all imported grammar files without duplicates"""
        with open(filename, 'r', encoding='utf-8') as inp:
            lines = inp.readlines()
        new_lines = []
        inc_lines = []
        for line in lines:
            match = re.search(self.__regex, line)
            if match:
                include = match.group(1).replace('.', '/') + '.tx'
                if include not in self.__memo:
                    self.__memo.add(include)
                    include_file = path.join(self.grammar_dir, include)
                    inc_lines.extend(self._expand_grammar(include_file))
            else:
                new_lines.append(line)
        new_lines.extend(inc_lines)
        return new_lines


def display_exception(func):
    """display exceptions raised in a function and bypassed by its caller"""
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            print('\n', file=sys.stderr)
            traceback.print_exception(*sys.exc_info(), file=sys.stderr)
            print('\n', file=sys.stderr)
            raise err
    return decorator


class TextXCompleter:
    """a completer for textX based languages to be used with readline"""
    matches = []

    def __init__(self, grammar_str, options=None, ids=None, console=None, **kwargs):
        self.options = options or []
        self.ids = ids or []
        self.meta = metamodel_from_str(grammar_str, **kwargs)
        self.logger = get_logger(__name__ + '.completer')
        self.console = console

    @property
    def buff(self):
        """return the multi-line buffer of an optional console as a string,
        default is empty string
        """
        if self.console:
            return '\n'.join(self.console.buffer)
        return ''

    def get_expected(self, text):
        """get a list of the expected string matches"""
        try:
            self.meta.model_from_str(self.buff + text)
        except TextXSyntaxError as err:
            strings = [str(r) for r in err.expected_rules if isinstance(r, StrMatch)]
            regexes = [str(r) for r in err.expected_rules if isinstance(r, RegExMatch)]
            strings = list(set(strings))
            regexes = list(set(regexes))
            self.logger.debug('regexes: %s', regexes)
            if r'[^\d\W]\w*\b' in regexes:
                strings.extend(self.ids)
            if r'(True|true|False|false|0|1)\b' in regexes:
                strings.extend(['true', 'false'])
            currpos = err.col - 1
            endidx = len(self.buff + text)
            offset = endidx - currpos
            self.logger.debug('currpos: %s', currpos)
            self.logger.debug('endidx: %s', endidx)
            self.logger.debug('offset: %s', offset)
            self.logger.debug('strings: %s', repr(strings))
            assert offset >= 0
            self.matches = []
            if offset == 0:
                for string in strings:
                    if string[0].isalpha() and text[-1].isalpha() or text[-1] in (',', ';'):
                        string = ' ' + string
                    self.matches.append(text + string)
                self.matches.extend([o for o in self.options if o.startswith(text)])
            else:
                for string in strings:
                    if string.startswith(text[-offset:].strip()):
                        self.matches.append(text[:-offset] + string + ' ')
            self.logger.debug('matches: %s', repr(self.matches))
        except TextXSemanticError:
            self.matches = [text]
            self.logger.debug('full match: %s', self.matches)
        else:
            self.matches = [text]
            self.logger.debug('full match: %s', self.matches)

    @display_exception
    def complete(self, text, state):
        """the main method as required by readline completer"""
        self.logger.debug('text: %s, state: %s', text, state)
        self.logger.debug('buffer: %s', repr(self.buff))
        if state == 0:
            self.matches = []
            stripped_text = text.strip()
            if stripped_text:
                self.get_expected(text)
            if not self.matches and not self.buff:
                self.matches = [o for o in self.options if o.startswith(stripped_text)]
                self.matches.extend([o for o in self.ids if o.startswith(stripped_text)])
        self.logger.debug('%s matches: %s', repr(text), self.matches)
        response = self.matches[state] if state < len(self.matches) else None
        self.logger.debug('complete %s', repr(response))
        return response

    def is_complete(self, text):
        """check whether more input is expected"""
        try:
            self.meta.model_from_str(text)
        except TextXSyntaxError as err:
            curr_line_len = len(text.split('\n')[-1])
            offset = curr_line_len - err.col + 1
            assert offset >= 0
            if offset == 0:
                return False
        except TextXSemanticError:
            pass
        return True
