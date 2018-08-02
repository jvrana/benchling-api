from benchlingapi.schema import FolderSchema
from benchlingapi.models import Folder


def test_tableize(session):
    assert session.Folder.tableize() == "folders"


def test_camelize(session):
    assert session.Folder.camelize() == "folders"


def test_camelize_id(session):
    assert session.Folder.camelize("id") == "folderIds"


def test_list(session):
    result = session.Folder.list()
    print(result)
    assert len(result) > 1
    assert isinstance(result[0], Folder)

def test_list_pages(session):
    pages = session.Folder.list_pages()
    p = next(pages)
    assert issubclass(type(p[0]), Folder)
    p2 = next(pages)
    assert issubclass(type(p2[0]), Folder)
    assert p[0].id != p2[0].id

def test_find_by_name(session):
    folder = session.Folder.find_by_name("Primers", projectId=session.Project.find_by_name("API_Folder").id)
    print(folder)