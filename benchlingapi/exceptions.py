r"""
Exceptions (:mod:`benchlingapi.exceptions`)
===========================================

.. currentmodule:: benchlingapi.exceptions

BenchlingAPI exceptions
"""


class BenchlingAPIException(Exception):
    """Generic Exception for BenchlingAPI."""


class BenchlingLoginError(BenchlingAPIException):
    """Errors for incorrect login credentials."""


class ModelNotFoundError(BenchlingAPIException):
    """Model not found."""


class SchemaNotFoundError(BenchlingAPIException):
    """Model not found."""


################################
# Benchling request exceptions
################################
class BenchlingServerException(BenchlingAPIException):
    """Exceptions received from the Benchling site."""


class RegistryException(BenchlingServerException):
    pass


class InvalidRegistryId(RegistryException):
    pass


class RegistryValidationError(RegistryException):
    pass


def exception_dispatch(exception_with_response):
    """Dispatches Benchling exceptions (from the site) to Pythonic
    exceptions."""
    e = exception_with_response
    try:
        error_data = e.response.json()
        user_msg = error_data["error"]["userMessage"]
        if "Invalid entityRegistryId" in user_msg:
            raise InvalidRegistryId(str(e)) from e
        elif (
            "That name is already used as either an alias or a name in this registry"
            in user_msg
        ):
            raise InvalidRegistryId(str(e)) from e
        elif "entities you attempted to register failed validation" in user_msg:
            raise RegistryValidationError(str(e)) from e
    except KeyError:
        pass
    raise e
