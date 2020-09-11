import pytest

from benchlingapi.exceptions import InvalidRegistryId


def test_get_entities_in_registry(session):

    registry = session.Registry.one()
    models = registry.get_entities(["aqKL003", "aqKL010", "aqqJV010"])
    print(models)


def test_invalid_registry(session):
    registries = session.Registry.all()
    for registry in registries:
        with pytest.raises(InvalidRegistryId):
            session.DNASequence.find_in_registry("adsklfherhg", registry_id=registry.id)


def test_list_all_in_registry(session):
    registry = session.Registry.one()
    n = 0
    for d in list(
        session.DNASequence.all(registry_id=registry.id, page_limit=10, limit=50)
    ):
        assert d.entity_registry_id
        assert d.registry_id == registry.id
        n += 1
    assert n == 50
