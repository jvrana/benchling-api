import pytest

from uuid import uuid4

from benchlingapi.models import models


def test_list_with_entityRegistryId(example_from_inventory):
    example_from_inventory( )
    dnas = session.DNASequence.list(registryId=session.Registry.list()[0].id)

    schemas = session.DNASequence.valid_schemas()
    print(schemas)
    d = session.DNASequence.registry_dict()
    print(d)

    list(d.values())[0].register()
