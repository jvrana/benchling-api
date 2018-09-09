import inflection
from marshmallow import class_registry
from marshmallow import __version__
from distutils.version import LooseVersion
from benchlingapi.exceptions import ModelNotFoundError
from benchlingapi.utils import url_build


class ModelRegistry(type):
    """Stores a list of models that can be accessed by name."""
    models = {}

    def __init__(cls, name, bases, nmspc):
        """Saves model to the registry"""
        super().__init__(name, bases, nmspc)
        if not name == "ModelBase":
            if name not in ModelRegistry.models:
                ModelRegistry.models[name] = cls

    @staticmethod
    def get_model(model_name):
        """Gets model by model_name"""
        if model_name not in ModelRegistry.models:
            raise ModelNotFoundError(
                "Model \"{}\" not found in ModelRegistry.".format(model_name))
        else:
            return ModelRegistry.models[model_name]

    def __getattr__(cls, item):
        """
        Special warning for attribute errors.
        Its likely that user may have wanted to use a model interface instead of
        the Base class.
        """
        raise AttributeError("'{0}' has no attribute '{1}'"
                             .format(cls.__name__, item))

    @property
    def model_name(cls):
        # if cls.alias is not None:
        #     return cls.alias
        return cls.__name__


class ModelBase(object, metaclass=ModelRegistry):
    # http = None  # initialized with Session calls a model interface
    session = None
    alias = None

    def __init__(self, **data):
        self.__dict__.update(data)

    @property
    def model_name(self):
        # if self.alias is not None:
        #     return self.alias
        return self.__class__.__name__

    @classmethod
    def schema(cls, *args, **kwargs):
        schema = class_registry.get_class(cls.__name__ + "Schema")
        schema_inst = schema(*args, **kwargs)
        schema_inst.context["session"] = cls.session
        return schema_inst

    # TODO: remove schema_loader for marshmallow > 3
    @staticmethod
    def schema_loader(schema_inst, data):
        result = schema_inst.load(data)
        if LooseVersion(__version__) < LooseVersion('3.0.0'):
            if len(result.errors) > 0:
                raise Exception(str(result.errors))
            return result.data
        return result

    # TODO: remove schema_dumper for marshmallow > 3
    @staticmethod
    def schema_dumper(schema_inst, inst):
        result = schema_inst.dump(inst)
        if LooseVersion(__version__) < LooseVersion('3.0.0'):
            if len(result.errors) > 0:
                raise Exception(str(result.errors))
            return result.data
        return result

    @classmethod
    def load(cls, data, *args, **kwargs):
        schema_inst = cls.schema(*args, **kwargs)
        inst = cls.schema_loader(schema_inst, data)
        inst.raw = data
        return inst

    @classmethod
    def load_many(cls, data, *args, **kwargs):
        schema_inst = cls.schema(*args, many=True, **kwargs)
        # TODO: change for marshmallow > v3
        insts = cls.schema_loader(schema_inst, data)
        for inst_data, inst in zip(data, insts):
            try:
                inst.raw = inst_data
            except:
                pass
        return insts

    @classmethod
    def tableize(cls):
        name = inflection.tableize(cls.__name__)
        name = inflection.dasherize(name)
        return name

    @classmethod
    def camelize(cls, property=None):
        name = inflection.underscore(cls.model_name)
        if property is not None:
            name += "_" + inflection.pluralize(property)
        else:
            name = inflection.pluralize(name)
        name = inflection.camelize(name)
        name = name[0].lower() + name[1:]
        return name

    @classmethod
    def path(cls, additional_paths=None):
        path = [cls.tableize()]
        if additional_paths is not None:
            if not isinstance(additional_paths, list):
                additional_paths = [additional_paths]
            path += additional_paths
        return url_build(*path)

    @classmethod
    def _get(cls, path_params=None, params=None, action=None):
        response = cls.session.http.get(cls.path(additional_paths=path_params), params=params, action=action)
        return response
        # return cls.load(response)

    @classmethod
    def _get_pages(cls, path_params=None, params=None, action=None):
        pages = cls.session.http.get_pages(cls.path(additional_paths=path_params), params=params, action=action)
        return pages

    @classmethod
    def _post(cls, data, path_params=None, params=None, action=None):
        response = cls.session.http.post(cls.path(additional_paths=path_params), json=data, params=params,
                                         action=action)
        return response

    @classmethod
    def _patch(cls, data, path_params=None, params=None, action=None):
        response = cls.session.http.patch(cls.path(additional_paths=path_params), json=data, params=params,
                                          action=action)
        return response

    @classmethod
    def list(cls, **params):
        response = cls._get(params=params)
        return cls.load_many(response[cls.camelize()])

    @classmethod
    def get(cls, id, **params):
        response = cls._get(id, params=params)
        return cls.load(response)

    @classmethod
    def find(cls, id, **params):
        return cls.get(id, **params)

    @classmethod
    def find_by_name(cls, name, **page_params):
        for page in cls.list_pages(**page_params):
            for inst in page:
                if inst.name == name:
                    return inst

    @classmethod
    def list_pages(cls, **params):
        generator = cls._get_pages(params=params)
        response = next(generator, None)
        while response is not None:
            yield cls.load_many(response[cls.camelize()])

            response = next(generator, None)

    @classmethod
    def update_model(cls, model_id, data, **params):
        response = cls._patch(data, path_params=[model_id], **params)
        return cls.load(response)

    @classmethod
    def create_model(cls, data, **params):
        response = cls._post(data, **params)
        return cls.load(response)

    def _create_from_data(self, data):
        r = self.create_model(data)
        self.__dict__.update(r.__dict__)
        return self

    def _update_from_data(self, data):
        r = self.update_model(self.id, data)
        self.__dict__.update(r.__dict__)
        return self

    # return cls._get_pages()

    # return cls._get(id)
    #
    # def bulk_get(self, ids):
    #     return self._get(params={self.camelize("id"): ids}, action="bulk-get")
    #
    # def create(self, data):
    #     return self._post(data)
    #
    # def bulk_create(self, data):
    #     return self._post(data, action="bulk-create")
    #
    # def update(self, id, data):
    #     return self._patch(data, path_params=id)

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.__class__.model_name}) at {id(self)}>"
