import inflection
from benchlingapi.exceptions import ModelNotFoundError


class ModelRegistry(type):
    """Stores a list of models that can be accessed by name."""
    models = {}

    def __init__(cls, name, bases, selfdict):
        """Saves model to the registry"""
        super().__init__(name, bases, selfdict)
        if not name == "ModelBase":
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
        raise AttributeError("'{0}' has no attribute '{1}'. Method may be a ModelInterface method."
                             " Did you mean '<yoursession>.{0}.{1}'?"
                             .format(cls.__name__, item))


class ModelBase(object):
    class ModelBase(object, metaclass=ModelRegistry):
        def __init__(self):
            self.http = None
            self.data = None

        @classmethod
        def path(cls):
            name = inflection.underscore(cls.__name__)
            name = inflection.dasherize(name)
            name = inflection.pluralize(name)
            return name

        @classmethod
        def all(cls, http):
            return http.post(cls.path())

        @classmethod
        def find(cls, http, model_id):
            return http.get(f"{cls.path()}/{model_id}")

        @classmethod
        def delete(cls, http, model_id):
            return http.delete(f"{cls.path()}/{model_id}")

        @classmethod
        def create(cls, http, json_data):
            return http.post(f"{cls.path()}", json_data=json_data)


class ModelInterface(object):

    def __init__(self, model_name, http):
        self.model_name = model_name
        self.http = http
        self.model = ModelRegistry.get_model(model_name)

    def all(self):
        return self.model.post(self.http)

    def find(self, model_id):
        return self.model.find(self.http, model_id)

    def delete(self, model_id):
        return self.model.delete(self.http, model_id)

    def create(self, json_data):
        return self.model.create(self.http, json_data)