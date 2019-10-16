from benchlingapi.models.base import ModelRegistry
from benchlingapi.models import models


def test__all__models_in_registry():
    missing_models = []
    for expected_model in models.__all__:
        if expected_model not in ModelRegistry.models:
            missing_models.append(expected_model)
    assert (
        not missing_models
    ), "There are models in __all__ that are missing from the ModelRegistry."


def test_models_registry_in__all__():
    missing_models = []
    for expected_model in ModelRegistry.models.values():
        if expected_model.__name__ not in models.__all__:
            missing_models.append(expected_model.__name__)
    assert (
        not missing_models
    ), "There are models in ModelRegistry that are missing from __all__."
