from benchlingapi.models import DNASequence, Annotation, Folder
from uuid import uuid4

from benchlingapi.models import DNASequence


def test_find(session):
    assert session.DNASequence.get('seq_6rvTvctB') is not None
    assert session.DNASequence.find('seq_6rvTvctB') is not None


def test_tableize(session):
    assert session.DNASequence.tableize() == "dna-sequences"


def test_camelize(session):
    assert session.DNASequence.camelize() == "dnaSequences"


def test_camelize_id(session):
    assert session.DNASequence.camelize("id") == "dnaSequenceIds"

def test_get(session):
    result = session.DNASequence.get("seq_6rvTvctB")
    print(result)

def test_save_new(session):
    new_dna = session.DNASequence(
        **{'aliases': [],
         'annotations': [],
         'bases': 'agtagatacgaa',
         'folderId': 'lib_Y8XL068P',
         'isCircular': False,
         'name': 'temp',
         'translations': []}
    )
    new_dna.save()
    assert new_dna.id is not None

def test_save(session):
    """Should copy"""
    result = session.DNASequence.get("seq_6rvTvctB")
    response = result.save()
    new_id = response.id
    assert new_id is not None
    assert new_id is not result.id

def test_create_new(session):

    folder = session.Folder.find_by_name("Primers", projectId=session.Project.find_by_name("API_Folder").id)
    annotation1 = {
        "color": "#FF9CCD",
        "end": 3,
        "name": "bla gene",
        "start": 1,
        "strand": 1,
        "type": "gene"
    }
    annotation2 = {
        "color": "#FF9CCD",
        "end": 5,
        "name": "bla gene",
        "start": 1,
        "strand": -1,
        "type": "gene"
    }
    new_seq = session.DNASequence(
        bases="AGCGTATGTGTGTA",
        name="MyNewSeq",
        isCircular=False,
        annotations=[annotation1, annotation2],
        folderId=folder.id
    )
    new_seq.save()
    assert new_seq.id is not None


def test_update(session):
    seq_id = "seq_6rvTvctB"
    result = session.DNASequence.get(seq_id)
    new_name = str(uuid4())
    result.name = new_name
    result.update()
    result2 = session.DNASequence.get(seq_id)
    assert result2.name == new_name


def test_reload(session):
    seq_id = "seq_6rvTvctB"
    result = session.DNASequence.get(seq_id)
    old_name = result.name
    new_name = str(uuid4())
    result.name = new_name

    # should restore to old_name
    assert not result.name == old_name
    result.reload()
    assert not result.name == new_name
    assert result.name == old_name


def test_from_share_link(session):
    dna = session.DNASequence.from_share_link("https://benchling.com/s/BKopv8ZH")
    assert issubclass(type(dna), DNASequence)


def test_list(session):
    result = session.DNASequence.list()
    print(result)
    assert len(result) > 1
    assert isinstance(result[0], DNASequence)


def test_list_pages(session):
    pages = session.DNASequence.list_pages()
    p = next(pages)
    assert issubclass(type(p[0]), DNASequence)
    p2 = next(pages)
    assert issubclass(type(p2[0]), DNASequence)
    assert p[0].id != p2[0].id


def test_nested_annotations(session):
    seq = session.DNASequence.find('seq_Gp4Goekc')

    assert isinstance(seq.annotations[0], Annotation)