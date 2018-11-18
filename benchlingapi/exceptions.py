"""
BenchlingAPI specific exceptions
"""

class BenchlingAPIException(Exception):
    """Generic Exception for BenchlingAPI"""


class BenchlingLoginError(Exception):
    """Errors for incorrect login credentials"""


# class AquariumLoginError(Exception):
#     """Errors for incorrect Aquarium login credentials"""


class ModelNotFoundError(Exception):
    """Model not found"""

class SchemaNotFoundError(Exception):
    """Model not found"""

################################
# Benchling request exceptions
################################
class BenchlingException(Exception):
    """Exceptions received from the Benchling site"""

class RegistryException(BenchlingException):
    pass


class InvalidRegistryId(RegistryException):
    pass


class RegistryValidationError(RegistryException):
    pass


def exception_dispatch(exception_with_response):
    """Dispatches Benchling exceptions (from the site) to Pythonic exceptions"""
    e = exception_with_response
    try:
        error_data = e.response.json()
        userMessage = error_data['error']['userMessage']
        if 'Invalid entityRegistryId' in userMessage:
            raise InvalidRegistryId(str(e)) from e
        elif 'entities you attempted to register failed validation' in userMessage:
            raise RegistryValidationError(str(e)) from e
    except KeyError:
        pass
    raise e