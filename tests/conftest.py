import json
import os

import pytest

from benchlingapi.session import Session
from benchlingapi.models.base import ModelRegistry
from benchlingapi.models import mixins


@pytest.fixture
def config():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    config_location = os.path.join(test_dir, "secrets/config.json")
    with open(config_location, 'rU') as handle:
        return json.load(handle)


@pytest.fixture(scope="session")
def session():
    return Session(config()["credentials"]["api_key"])


@pytest.fixture(scope="session")
def project(session):
    project_info = config()['project']
    project = session.Project.find_by_name(project_info['name'])
    if project is None:
        pytest.skip("Could not find project for {}".format(project_info))
    return project


@pytest.fixture(scope="session")
def inv_folder(session, project):
    folder_config = config()['inventory_folder']

    folder = session.Folder.find_by_name(folder_config['name'], projectId=project.id)
    if folder is None:
        pytest.skip("Could not find folder for {}. Please create folder to continue testing.".format(folder_config))

    assert folder.name == "API_Inventory"
    assert session.Project.find(folder.projectId).name == project.name

    return folder


def clean_up_folder(folder):
    # clean up trash folder
    print("Cleaning trash folder")
    entity_models = ModelRegistry.filter_models_by_base_classes([mixins.InventoryEntityMixin])
    for model in entity_models:

        interface = folder.session.interface(model.__name__)
        print("Archiving \"{}\" models...".format(model.__name__))
        for m in interface.all(folderId=folder.id):
            print("Archiving {}".format(m))
            m.archive(m.ARCHIVE_REASONS.OTHER)


def populate_folder(folder, inventory_folder):
    for m in inventory_folder.all_entities():
        print("Copying {} from {} to {}".format(m, folder.name, inventory_folder.name))
        m_copy = m.copy()
        m_copy.folderId = folder.id
        m_copy.save()


@pytest.fixture(scope="session", autouse=False)
def trash_folder(session, project, inv_folder):
    """The session-wide testing folder. All entities in the folder get archived
     at the end of every session."""
    folder_config = config()['trash_folder']

    folder = session.Folder.find_by_name(folder_config['name'], projectId=project.id)
    if folder is None:
        pytest.skip("Could not find folder for {}. Please create folder to continue testing.".format(folder_config))

    assert folder.name == "API_Trash"
    assert session.Project.find(folder.projectId).name == project.name

    # populating trash folder
    # populate_folder(folder, inv_folder)

    yield folder

    clean_up_folder(folder)


@pytest.fixture(scope="function")
def example_from_inventory(model, inv_folder, trash_folder):
    """Returns a copied example from the inventory folder given a Model class"""
    interface = inv_folder.session.interface(model.__name__)
    example = interface.one(folderId=inv_folder.id)
    if example is None:
        pytest.skip("Could not find an example entity for \"{}\" in \"{}\"".format(model, inv_folder.name))
    example_copy = example.copy()
    example_copy.folderId = trash_folder.id
    data = example_copy.dump(**example_copy.CREATE_SCHEMA)
    example_copy.save()
    return example_copy