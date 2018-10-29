import inspect
from functools import reduce
from uuid import uuid4

import pytest

from benchlingapi.models import ModelRegistry
from benchlingapi.models.mixins import ListMixin, GetMixin, CreateMixin, ArchiveMixin, RegistryMixin, EntityMixin

models_by_base_classes = {}
for m in ModelRegistry.models.values():
    hierarchy = inspect.getmro(m)
    for base_model in hierarchy:
        models_by_base_classes.setdefault(base_model.__name__, []).append(m)


def pytest_generate_tests(metafunc):
    # parameterize with models that match the expected model test
    only = metafunc.cls.only
    if isinstance(only, list):
        model_sets = []
        for only_model in only:
            model_sets.append(set(models_by_base_classes[only_model.__name__]))
        models = reduce(lambda x, y: x.intersection(y), model_sets)
    else:
        models = models_by_base_classes[only.__name__]

    create_params_dict = metafunc.cls.__dict__.get('create_params', {})
    create_params = [create_params_dict.get(m.__name__, None) for m in models]

    argdict = {'model': [], 'create_params': []}
    for m in models:
        create_params = create_params_dict.get(m.__name__, None)
        if isinstance(create_params, list):
            for cp in create_params:
                argdict['model'].append(m)
                argdict['create_params'].append(cp)
        else:
            argdict['model'].append(m)
            argdict['create_params'].append(create_params)

    argnames = [n for n in metafunc.funcargnames if n in argdict]
    argvalues = zip(*[argdict[n] for n in argnames])

    if len(argnames) == 1:
        argvalues = [a[0] for a in argvalues]

    metafunc.parametrize(','.join(argnames), argvalues, scope="class")


class HasInterface:

    @pytest.fixture(scope="function")
    def interface(self, session, model):
        return session.interface(model.__name__)


class HasExample(HasInterface):

    @pytest.fixture(scope="function")
    def example_model(self, interface, model):
        one = interface.one()
        if not one:
            pytest.skip("Model \"{}\" not found".format(model.__name__))
        return one


class TestListMixin(HasExample):
    only = ListMixin

    def test_one(self, example_model):
        assert example_model

    def test_last_1(self, interface, model):
        size1 = interface.last(1)
        assert 1 == len(size1)
        assert isinstance(size1[0], model)

    def test_last_20(self, interface, model):
        size20 = interface.last(20)
        assert len(size20) == 20
        assert isinstance(size20[-1], model)

    def test_find_by_name(self, interface, model, example_model):
        found = interface.find_by_name(example_model.name)
        for f in found:
            assert f.name == example_model.name
            assert isinstance(f, model)


class TestGetMixin(HasExample):
    only = [ListMixin, GetMixin]

    def test_find(self, interface, example_model):
        assert interface.get(example_model.id) is not None
        assert interface.find(example_model.id) is not None
        assert interface.find(str(uuid4())) is None


class TestEntity(HasInterface):
    only = EntityMixin

    @pytest.fixture(scope="function")
    def example_model(self, interface, model):
        one = interface.one()
        if not one:
            pytest.skip("Model \"{}\" not found".format(model.__name__))
        return one

    def test_find_by_name(self, session, interface, model, example_model):
        if not example_model:
            pytest.skip("Model \"{}\" not found".format(model.__name__))
        found = interface.find_by_name(example_model.name)
        assert len(found) > 0
        assert example_model.id in [e.id for e in found]
        assert interface.find_by_name(str(uuid4())) == []

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
            annotations=[
                {
                    "color": "#FF9CCD",
                    "end": 3,
                    "name": "bla gene",
                    "start": 1,
                    "strand": 1,
                    "type": "gene"
                },
                {
                    "color": "#FF9CCD",
                    "end": 5,
                    "name": "bla gene",
                    "start": 1,
                    "strand": -1,
                    "type": "gene"
                }
            ]
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
                    "type": "gene"
                }
            ],
            name="MyProtein"
        )
    }

    @pytest.fixture(scope="function")
    def create_param(self, session, trash_folder, create_params):
        create_params['folderId'] = trash_folder.id
        return create_params

    def test_create(self, interface, create_param):
        new_model = interface(
            **create_param
        )
        new_model.save()


class TestArchiveMixin(HasInterface):

    only=[ArchiveMixin, ListMixin]

    @pytest.fixture(scope='function')
    def example(self, interface, trash_folder, model):
        one = interface.one(folderId=trash_folder.id)
        if one is None:
            pytest.skip("No model in test folder could be found.")
        return one

    def test_example(self, interface, example):
        assert not example.is_archived
        example.archive()
        assert example.is_archived

    def test_list_archived(self, interface):
        archived = interface.list_archived()
        assert len(archived) > 1


class TestRegistryMixin(HasInterface):
    only = [RegistryMixin, CreateMixin]

    @pytest.fixture(scope='function')
    def example(self, interface, inv_folder, model):
        one = interface.one(folderId=inv_folder.id)
        if one is None:
            pytest.skip("No model in test folder could be found.")
        return one

    def test_print_valid_schemas(self, example):
        example.print_valid_schemas()

    @pytest.fixture(scope='function')
    def copy_sample(self, example, interface):
        example_copy = example.copy()
        example_copy.save()
        assert example_copy.id
        assert example_copy.id != example.id
        return example_copy

    def test_register(self, copy_sample):
        valid_schemas = copy_sample.valid_schemas
        assert not copy_sample.is_registered
        copy_sample.set_schema(valid_schemas[0][1]['name'])
        copy_sample.register()
        assert copy_sample.is_registered

    def test_unregister(self, model):
        pass