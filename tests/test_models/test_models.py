import pytest

from benchlingapi.models import ModelRegistry
from benchlingapi.models.mixins import ArchiveMixin
from benchlingapi.models.mixins import CreateMixin
from benchlingapi.models.mixins import EntityMixin
from benchlingapi.models.mixins import GetMixin
from benchlingapi.models.mixins import InventoryMixin
from benchlingapi.models.mixins import ListMixin
from benchlingapi.models.mixins import RegistryMixin
from benchlingapi.models.models import Folder
from benchlingapi.models.models import Project


def pytest_generate_tests(metafunc):
    # parameterize with models that match the expected model test
    only_models = ModelRegistry.filter_models_by_base_classes(metafunc.cls.only)

    create_params_dict = metafunc.cls.__dict__.get("create_params", {})

    argdict = {"model": [], "create_params": []}
    for m in only_models:
        create_params = create_params_dict.get(m.__name__, None)
        if isinstance(create_params, list):
            for cp in create_params:
                argdict["model"].append(m)
                argdict["create_params"].append(cp)
        else:
            argdict["model"].append(m)
            argdict["create_params"].append(create_params)

    argnames = [n for n in metafunc.fixturenames if n in argdict]
    argvalues = zip(*[argdict[n] for n in argnames])

    if len(argnames) == 1:
        argvalues = [a[0] for a in argvalues]

    metafunc.parametrize(",".join(argnames), argvalues, scope="class")


class HasInterface:
    @pytest.fixture(scope="function")
    def interface(self, session, model):
        return session.interface(model.__name__)


class HasExample(HasInterface):
    @pytest.fixture(scope="function")
    def example_model(self, interface, model):
        one = interface.one()
        if not one:
            pytest.skip('Example model "{}" not found'.format(model.__name__))
        return one


class TestListMixin(HasExample):
    only = ListMixin

    def test_one(self, example_model):
        assert example_model

    def test_last_1(self, interface, model):
        size1 = interface.last(1)
        if len(size1) == 0:
            pytest.skip('No models found for "{}"'.format(model))
        assert 1 == len(size1)
        assert isinstance(size1[0], model)

    def test_last_20(self, interface, model):
        size20 = interface.last(20)
        if len(size20) == 0:
            pytest.skip('No models found for "{}"'.format(model))
        size_list = interface.list()
        assert min(len(size20), len(size_list)) <= 20
        assert isinstance(size20[-1], model)

    def test_find_by_name(self, interface, model, example_model):
        found = interface.find_by_name(example_model.name)
        assert found.name == example_model.name
        assert isinstance(found, model)

    def test_list_pages(self, interface, model):
        list(interface.list_pages(page_limit=1, page_size=1))


class TestGetMixin(HasExample):
    only = [ListMixin, GetMixin]

    def test_find(self, interface, example_model):
        assert interface.get(example_model.id) is not None
        assert interface.find(example_model.id) is not None
        assert interface.find("asdf98qw4hotnof8gyh") is None


class TestEntity(HasInterface):
    only = EntityMixin

    @pytest.fixture(scope="function")
    def example_model(self, interface, model):
        one = interface.one()
        if not one:
            pytest.skip('Example model "{}" not found'.format(model.__name__))
        return one

    def test_find_by_name(self, session, interface, model, example_model):
        if not example_model:
            pytest.skip('Example model "{}" not found'.format(model.__name__))
        found = interface.find_by_name(example_model.name)
        assert found
        assert example_model.id == found.id
        assert interface.find_by_name("alsjdfoijewfosdiufoasdf") is None

    def test_batches(self, example_model):
        batches = example_model.batches()
        assert isinstance(batches, list)


class TestCreateMixin(HasInterface):

    only = CreateMixin

    create_params = {
        "DNASequence": dict(
            bases="AGCGTATGTGTGTA",
            name="MyNewSeq",
            isCircular=False,
            schemaId=None,
            annotations=[
                {
                    "color": "#FF9CCD",
                    "end": 3,
                    "name": "bla gene",
                    "start": 1,
                    "strand": 1,
                    "type": "gene",
                },
                {
                    "color": "#FF9CCD",
                    "end": 5,
                    "name": "bla gene",
                    "start": 1,
                    "strand": -1,
                    "type": "gene",
                },
            ],
        ),
        "AASequence": dict(
            aminoAcids="AMVGKLALDLSD",
            annotations=[
                {
                    "color": "#FF9CCD",
                    "end": 5,
                    "name": "bla gene",
                    "start": 1,
                    "strand": -1,
                    "type": "gene",
                }
            ],
            schemaId=None,
            name="MyProtein",
        ),
        "CustomEntity": dict(name="MyEntity", aliases=[], schemaId=None),
        "Batch": dict(entityId="seq_342322", fields={}),
        "Oligo": dict(name="MyOligo", bases="AGTAGCATG"),
    }

    @pytest.fixture(scope="function")
    def create_param(self, session, trash_folder, create_params, interface):
        create_params["folderId"] = trash_folder.id
        if "schemaId" in create_params:
            schema = interface.valid_schemas()[0][1]
            create_params["schemaId"] = schema["id"]
        if "entityId" in create_params:
            entity = session.CustomEntity.one()
            create_params["entityId"] = entity.id
        return create_params

    def test_model_constructor(self, interface, create_param):
        new_model = interface(**create_param)
        assert new_model

    def test_model_save(self, interface, create_param):
        new_model = interface(**create_param)
        new_model.save()
        assert new_model.id


class TestArchiveMixin(HasInterface):

    only = [ArchiveMixin, ListMixin, InventoryMixin]

    @pytest.fixture(scope="function")
    def example(self, model, example_from_inventory):
        if model not in [Project, Folder]:
            return example_from_inventory
        else:
            pytest.skip('Skipping "{}"'.format(model))

    def test_archive(self, interface, example):
        assert not example.is_archived
        example.archive()
        assert example.is_archived
        example.unarchive()
        assert not example.is_archived

    # def test_list_archived(self, interface):
    #     archived = interface.list_archived()
    #     assert len(archived) > 1


class TestRegistryMixin(HasInterface):
    only = [RegistryMixin, CreateMixin, ListMixin, InventoryMixin]

    @pytest.fixture(scope="function")
    def example(self, model, example_from_inventory):
        if model not in [Project, Folder]:
            return example_from_inventory
        else:
            pytest.skip('Skipping "{}"'.format(model))

    def test_print_valid_schemas(self, example):
        example.print_valid_schemas()

    @pytest.fixture(scope="function")
    def copy_sample(self, example, interface):
        example_copy = example.copy()
        example_copy.save()
        assert example_copy.id
        assert example_copy.id != example.id
        return example_copy

    def test_register(self, copy_sample, trash_folder):
        valid_schemas = copy_sample.valid_schemas
        assert not copy_sample.is_registered
        copy_sample.set_schema(valid_schemas()[0][1]["name"])
        copy_sample.register()
        assert copy_sample.is_registered
        copy_sample.unregister(trash_folder.id)
        assert not copy_sample.is_registered

#
# def test_dna_share_link(session):
#     return
#     # dnas = session.DNASequence.last(10)
#     # for dna in dnas:
#     #     assert dna
#     #     loaded = session.DNASequence.from_share_link(dna.web_url)
#     #     assert loaded.id == dna.id