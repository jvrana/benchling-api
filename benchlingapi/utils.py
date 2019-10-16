r"""
Utilities (:mod:`benchlingapi.utils`)
=============================

.. currentmodule:: benchlingapi.utils

"""
import inflection


def url_build(*parts):
    """Join parts of a url into a string."""
    return "/".join(p.strip("/") for p in parts)


def underscore(k):
    return inflection.underscore(k)


def underscore_keys(d):
    if d is not None:
        return {underscore(k): v for k, v in d.items()}


def un_underscore(k):
    s = inflection.camelize(k)
    s = s[0].lower() + s[1:]
    return s


def un_underscore_keys(d):
    if d is not None:
        return {un_underscore(k): v for k, v in d.items()}
