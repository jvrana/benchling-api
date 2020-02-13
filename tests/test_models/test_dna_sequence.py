import pytest


def test_web_link(session):
    dnas = session.DNASequence.last(10)

    for dna in dnas:
        loaded = session.DNASequence.from_share_link(dna.web_url)
        assert loaded.id == dna.id


# def test_share_link(session):
#
#     # dna = session.DNASequence.from_share_link('https://benchling.com/s/seq-YR1KBSvPlZ8sGOlnOBqe')
#     # assert dna
#     dna = session.DNASequence.one()
#     print(session.DNASequence.find(dna.id))
#     print(session.DNASequence.find('seq_Kzxlbux9'))
#
#     # print(session.Folder.find('lib_SjLcTsG4'))
#
#     folder = session.Folder.find_by_name('APITrash')
#     print(folder)
#     print(folder.id)
#     print(session.Folder.find(folder.id))
