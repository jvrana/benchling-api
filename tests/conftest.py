import json
import os

import pytest

from benchlingapi.session import Session


@pytest.fixture
def config():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    config_location = os.path.join(test_dir, "secrets/config.json")
    with open(config_location, 'rU') as handle:
        return json.load(handle)


@pytest.fixture(scope="module")
def session():
    return Session(config()["credentials"]["api_key"])


@pytest.fixture(scope="module")
def trash_folder(session):
    folder_config = config()['trash_folder']
    project_info = config()['project']

    project = session.Project.find_by_name(project_info['name'])[0]
    if project is None:
        pytest.skip("Could not find project for {}".format(folder_config))

    folder = session.Folder.find_by_name(folder_config['name'], projectId=project.id)[0]
    if folder is None:
        pytest.skip("Could not find folder for {}".format(folder_config))

    assert folder.name == "API_Trash"
    assert session.Project.find(folder.projectId).name == project.name

    return folder


@pytest.fixture(scope="module")
def inv_folder(session):
    folder_config = config()['inventory_folder']
    project = config()['project']

    project = session.Project.find_by_name(project['name'])[0]
    if project is None:
        pytest.skip("Could not find project for {}".format(folder_config))

    folder = session.Folder.find_by_name(folder_config['name'], projectId=project.id)[0]
    if folder is None:
        pytest.skip("Could not find folder for {}".format(folder_config))

    assert folder.name == "API_Inventory"
    assert session.Project.find(folder.projectId).name == project.name

    return folder

