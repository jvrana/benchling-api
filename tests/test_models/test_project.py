from benchlingapi.schema import ProjectSchema
from benchlingapi.models import Project


def test_tableize(session):
    assert session.Project.tableize() == "projects"


def test_camelize(session):
    assert session.Project.camelize() == "projects"


def test_camelize_id(session):
    assert session.Project.camelize("id") == "projectIds"


def test_list(session):
    result = session.Project.list()
    print(result)
    assert len(result) > 1
    assert isinstance(result[0], Project)

def test_list_pages(session):
    pages = session.Project.list_pages()
    p = next(pages)
    assert issubclass(type(p[0]), Project)
    p2 = next(pages)
    assert issubclass(type(p2[0]), Project)
    assert p[0].id != p2[0].id

def test_find_by_name(session):
    project = session.Project.find_by_name("API_Folder")
    print(project.id)
    assert issubclass(type(project), Project)