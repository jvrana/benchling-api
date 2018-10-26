from benchlingapi.models import Registry


def test_get(session):
    result = session.Registry.list()
    print(result)
    assert isinstance(result[0], Registry)


def test_get_entity_schemas(session):

    result = session.Registry.list()[0]
    print(result.entity_schemas)


def test_register_new_entity(session):

    registry = session.Registry.list()[0]
    schema = registry.get_schema("Aquarium DNA")

    dna = session.DNASequence.find('seq_LGALNruO')

    dna.schemaId = schema['id']

    dna.update()

    dna.unregister(session.Folder.find_by_name("APITrash").id)

    # registry.registry_entities([dna.id])

    # dna.unregister()
