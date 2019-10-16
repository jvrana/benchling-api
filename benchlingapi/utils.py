r"""
Utilities (:mod:`benchlingapi.utils`)
=====================================

.. currentmodule:: benchlingapi.utils

"""
import inflection


def url_build(*parts):
    """Join parts of a url into a string."""
    return "/".join(p.strip("/") for p in parts)


def underscore(k):
    """Transform keys like 'benchlingKey' to 'benchling_key'."""
    return inflection.underscore(k)


def un_underscore(k):
    """Transform keys like 'benchling_key' to 'benchlingKey'."""
    s = inflection.camelize(k)
    s = s[0].lower() + s[1:]
    return s


def _recursive_apply_to_keys(data, func, self_func):
    new_data = {}
    if data is not None:
        for k, v in data.items():
            if isinstance(v, dict):
                new_data[func(k)] = self_func(v)
            else:
                new_data[func(k)] = v
        return new_data
    return data


def underscore_keys(data):
    """Recursively transform keys to underscore format."""
    return _recursive_apply_to_keys(data, underscore, underscore_keys)


def un_underscore_keys(data):
    """Recursively un-transfrom keys from underscore format to benchling
    format."""
    return _recursive_apply_to_keys(data, un_underscore, underscore_keys)
