

def test_get_entities_in_registry(session):

    registry = session.Registry.one()
    models = registry.get_entities(['aqKL003', 'aqKL010', 'aqqJV010'])
    pass