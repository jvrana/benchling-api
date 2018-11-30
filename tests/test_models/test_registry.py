import pytest
from benchlingapi.exceptions import InvalidRegistryId


def test_get_entities_in_registry(session):

    registry = session.Registry.one()
    models = registry.get_entities(['aqKL003', 'aqKL010', 'aqqJV010'])
    pass

def test_invalid_registry(session):
    registries = session.Registry.all()
    for registry in registries:
        with pytest.raises(InvalidRegistryId):
            session.DNASequence.find_in_registry('adsklfherhg', registry_id=registry.id)
