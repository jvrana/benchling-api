r"""
Exceptions (:mod:`benchlingapi.exceptions`)
===========================================

.. currentmodule:: benchlingapi.exceptions

BenchlingAPI exceptions
"""


class BenchlingAPIException(Exception):
    """Generic Exception for BenchlingAPI caused from the Python API itself."""


class BenchlingLoginError(BenchlingAPIException):
    """Errors for incorrect login credentials."""


class ModelNotFoundError(BenchlingAPIException):
    """Model not found."""


class SchemaNotFoundError(BenchlingAPIException):
    """Schema not found."""


################################
# Benchling request exceptions
################################
class BenchlingServerException(BenchlingAPIException):
    """Exceptions received from the Benchling site."""


class InvalidRegistryId(BenchlingServerException):
    """Invalid registry id.

    Id or name exists in the registry.
    """


class RegistryValidationError(BenchlingServerException):
    """Entities do not match the expected registry schema."""


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
