from benchlingapi.schema import AASequenceSchema
from benchlingapi.models import AASequence


def test_tableize(session):
    assert session.AASequence.tableize() == "aa-sequences"


def test_camelize(session):
    assert session.AASequence.camelize() == "aaSequences"


def test_camelize_id(session):
    assert session.AASequence.camelize("id") == "aaSequenceIds"


def test_list(session):
    result = session.AASequence.list()
    print(result)
    assert len(result) > 1
    assert isinstance(result[0], AASequence)

def test_list_pages(session):
    pages = session.AASequence.list_pages()
    p = next(pages)
    assert issubclass(type(p[0]), AASequence)
    p2 = next(pages)
    assert issubclass(type(p2[0]), AASequence)
    assert p[0].id != p2[0].id