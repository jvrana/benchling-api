"""The base model class and registry for all model instances."""
import inspect
from distutils.version import LooseVersion
from functools import reduce

import inflection
from marshmallow import __version__
from marshmallow import class_registry

from benchlingapi.exceptions import ModelNotFoundError
from benchlingapi.utils import un_underscore_keys
from benchlingapi.utils import underscore_keys
from benchlingapi.utils import url_build


class ModelRegistry(type):
    """Stores a list of models that can be accessed by name."""

    models = {}

    def __init__(cls, name, bases, nmspc):
        """Saves model to the registry."""
        super().__init__(name, bases, nmspc)
        if not name == "ModelBase":
            if name not in ModelRegistry.models:
                ModelRegistry.models[name] = cls

    @staticmethod
    def get_model(model_name):
        """Gets model by model_name."""
        if model_name not in ModelRegistry.models:
            raise ModelNotFoundError(
                'Model "{}" not found in ModelRegistry.'.format(model_name)
            )
        else:
            return ModelRegistry.models[model_name]

    @staticmethod
    def models_by_base_classes():
        models_by_base_classes = {}
        for m in ModelRegistry.models.values():
            hierarchy = inspect.getmro(m)
            for base_model in hierarchy:
                models_by_base_classes.setdefault(base_model.__name__, []).append(m)
        return models_by_base_classes

    @staticmethod
    def filter_models_by_base_classes(bases):
        """Filters models registered in the model registry by their base
        classes.

        :param bases: base classes
        :type bases: type, list, or tuple
        :return: type
        :rtype: list
        """
        if isinstance(bases, list):
            model_sets = []
            for only_model in bases:
                model_sets.append(
                    set(ModelRegistry.models_by_base_classes()[only_model.__name__])
                )
            models = reduce(lambda x, y: x.intersection(y), model_sets)
        else:
            models = ModelRegistry.models_by_base_classes()[bases.__name__]
        return models

    def __getattr__(cls, item):
        """Special warning for attribute errors.

        Its likely that user may have wanted to use a model interface
        instead of the Base class.
        """
        raise AttributeError("'{}' has no attribute '{}'".format(cls.__name__, item))

    @property
    def model_name(cls):
        """Return this model's name."""
        return cls.__name__


class ModelBaseABC:
    """The model base for all BenchlingAPI model instances."""

    # http = None  # initialized with Session calls a model interface
    session = None
    alias = None

    def __init__(self, **data):
        data = underscore_keys(data)
        for k, v in data.items():
            setattr(self, k, v)

    @staticmethod
    def _url_build(*parts):
        return url_build(*parts)

    @property
    def model_name(self):
        # if self.alias is not None:
        #     return self.alias
        return self.__class__.__name__

    @classmethod
    def _serialization_schema(cls, *args, **kwargs):
        schema = class_registry.get_class(cls.__name__ + "Schema")
        schema_inst = schema(*args, **kwargs)
        schema_inst.context["session"] = cls.session
        return schema_inst

    # TODO: remove schema_loader for marshmallow > 3
    @staticmethod
    def _deserializer(schema_inst, data):
        if isinstance(data, list):
            data = [underscore_keys(d) for d in data]
        else:
            data = underscore_keys(data)
        result = schema_inst.load(data)
        if LooseVersion(__version__) < LooseVersion("3.0.0"):
            if len(result.errors) > 0:
                raise Exception(str(result.errors))
            result = result.data
        return result

    # TODO: remove schema_dumper for marshmallow > 3
    @staticmethod
    def _serializer(schema_inst, inst):
        result = schema_inst.dump(inst)
        if LooseVersion(__version__) < LooseVersion("3.0.0"):
            if len(result.errors) > 0:
                raise Exception(str(result.errors))
            result = result.data
        if isinstance(result, list):
            return [un_underscore_keys(d) for d in result]
        return un_underscore_keys(result)

    @classmethod
    def load(cls, data, *args, **kwargs):
        schema_inst = cls._serialization_schema(*args, **kwargs)
        inst = cls._deserializer(schema_inst, data)
        inst.raw = data
        return inst

    def dump(self, *args, **kwargs):
        schema = self._serialization_schema(*args, **kwargs)
        data = self._serializer(schema, self)
        return data

    @classmethod
    def load_many(cls, data, *args, **kwargs):
        schema_inst = cls._serialization_schema(*args, many=True, **kwargs)
        # TODO: change for marshmallow > v3
        insts = cls._deserializer(schema_inst, data)
        for inst_data, inst in zip(data, insts):
            if issubclass(type(inst), ModelBase):
                inst.raw = inst_data
        return insts

    @classmethod
    def _tableize(cls):
        """Tableize the model name.

        :return:
        """
        name = inflection.tableize(cls.__name__)
        name = inflection.dasherize(name)
        return name

    @classmethod
    def _camelize(cls, property=None):
        """Camelize the model name.

        :param property:
        :return:
        """
        name = inflection.underscore(cls.model_name)
        if property is not None:
            name += "_" + inflection.pluralize(property)
        else:
            name = inflection.pluralize(name)
        name = inflection.camelize(name)
        name = name[0].lower() + name[1:]
        return name

    @classmethod
    def _path(cls, additional_paths=None):
        path = [cls._tableize()]
        if additional_paths is not None:
            if not isinstance(additional_paths, list):
                additional_paths = [additional_paths]
            path += additional_paths
        return cls._url_build(*path)

    def _update_from_other(self, other):
        vars(self).update(vars(other))

    def reload(self):
        seq = self.find(self.id)
        self._update_from_other(seq)
        return self

    @classmethod
    def _get(cls, path_params=None, params=None, action=None):
        response = cls.session.http.get(
            cls._path(additional_paths=path_params), params=params, action=action
        )
        return response
        # return cls.load(response)

    @classmethod
    def _get_pages(cls, path_params=None, params=None, action=None):
        pages = cls.session.http.get_pages(
            cls._path(additional_paths=path_params), params=params, action=action
        )
        return pages

    @classmethod
    def _post(cls, data, path_params=None, params=None, action=None):
        response = cls.session.http.post(
            cls._path(additional_paths=path_params),
            json=data,
            params=params,
            action=action,
        )
        return response

    @classmethod
    def _patch(cls, data, path_params=None, params=None, action=None):
        response = cls.session.http.patch(
            cls._path(additional_paths=path_params),
            json=data,
            params=params,
            action=action,
        )
        return response

    @classmethod
    def _delete(cls, path_params=None, params=None, action=None):
        response = cls.session.http.delete(
            cls._path(additional_paths=path_params), params=params, action=action
        )
        return response

    def copy(self):
        return self.load(self.dump())

    def __repr__(self):
        return "<{cls} ({name}) at {id}>".format(
            cls=self.__class__.__name__, name=self.__class__.model_name, id=id(self)
        )


class ModelBase(ModelBaseABC, metaclass=ModelRegistry):
    """Registered model base for BenchlingAPI."""

    pass
