"""utility functions for work with nested lists"""


def list_apply(func, obj):
    """apply a function to all elements of an arbitrarily nested list"""
    if isinstance(obj, list):
        return [list_apply(func, x) for x in obj]
    return func(obj)


def list_flatten(lst):
    """get a flat list out from an arbitrarily nested list"""
    def flatten(lst):
        for elem in lst:
            if isinstance(elem, (list, tuple)):
                yield from flatten(elem)
            else:
                yield elem
    return list(flatten(lst))


def get_array_aslist(elements):
    """construct one list containing all nested lists for array objects"""
    alist = []
    for elem in elements:
        if isinstance(elem, (bool, int, str, float)):
            val = elem
        elif hasattr(elem, 'elements'):
            val = get_array_aslist(elem.elements)
        else:
            val = elem.value
        alist.append(val)
    return alist


def duplicates(iterable):
    """return a list of duplicated elements in an iterable"""
    seen = set()
    return [x for x in iterable if x in seen or seen.add(x)]
