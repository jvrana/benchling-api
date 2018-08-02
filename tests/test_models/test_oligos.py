from benchlingapi.schema import OligoSchema
from benchlingapi.models import Oligo


def test_tableize(session):
    assert session.Oligo.tableize() == "oligos"


def test_camelize(session):
    assert session.Oligo.camelize() == "oligos"


def test_camelize_id(session):
    assert session.Oligo.camelize("id") == "oligoIds"


def test_get(session):
    result = session.Oligo.get("seq_QzlmZ3zV")
    print(result)
