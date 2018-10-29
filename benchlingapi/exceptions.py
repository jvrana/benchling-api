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