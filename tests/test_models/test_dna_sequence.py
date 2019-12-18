import pytest


def test_share_link(session):
    dnas = session.DNASequence.last(10)

    for dna in dnas:
        loaded = session.DNASequence.from_share_link(dna.web_url)
        assert loaded.id == dna.id