"""
Exposes models to various API endpoints.
"""

from benchlingapi.models.base import ModelRegistry
from benchlingapi.exceptions import BenchlingAPIException, BenchlingException


class GetMixin:
    """
    Exposes the `get` and `find` by id methods
    """

    @classmethod
    def get(cls, id, **params):
        try:
            response = cls._get(id, params=params)
        except BenchlingAPIException as e:
            if e.response.status_code == 404:
                return None
            raise e
        return cls.load(response)

    @classmethod
    def find(cls, id, **params):
        return cls.get(id, **params)


class ListMixin:
    """
    Exposes the methods that return many model instances (e.g. `all`, `list`, `one`, etc.)
    """

    MAX_PAGE_SIZE = 100

    @classmethod
    def list(cls, **params):
        response = cls._get(params=params)
        return cls.load_many(response[cls.camelize()])

    @classmethod
    def one(cls, **params):
        """Return a single example model (default: most recent)"""
        models = cls.list(pageSize=1, **params)
        if len(models) == 0:
            return None
        return models[0]

    @classmethod
    def list_pages(cls, page_limit=None, **params):
        generator = cls._get_pages(params=params)
        response = next(generator, None)
        page_num = 1
        while response is not None and (page_limit is None or page_num <= page_limit):
            yield cls.load_many(response[cls.camelize()])
            response = next(generator, None)
            page_num += 1

    @classmethod
    def all(cls, page_limit=None, limit=None, **params):
        num = 0
        for page in cls.list_pages(page_limit=page_limit, **params):
            for m in page:
                yield m
                num += 1
                if limit is not None and num >= limit:
                    return

    @classmethod
    def last(cls, num, **params):
        """
        Returns the most recent models.

        :param num: number of models to return
        :type num: int
        :param params: additional search parameters
        :type params: dict
        :return: list of models
        :rtype: list
        """
        max_page_size = min(cls.MAX_PAGE_SIZE, params.get("pageSize", cls.MAX_PAGE_SIZE))
        if num <= max_page_size:
            max_page_size = num
        return list(cls.all(pageSize=max_page_size, limit=num))

    @classmethod
    def one(cls):
        models = cls.last(1)
        if models:
            return models[0]

    @classmethod
    def search(cls, fxn, limit=1, page_limit=5, **params):
        found = []
        for model in cls.all(page_limit=page_limit, **params):
            if fxn(model):
                found.append(model)
            if len(found) >= limit:
                return found
        return found

    @classmethod
    def find_by_name(cls, name, page_limit=5, **params):
        models = cls.search(lambda x: x.name == name, limit=1, page_limit=page_limit, **params)
        if models:
            return models[0]

    @classmethod
    def get(cls, id, **params):
        models = cls.search(lambda x: x.id == id, limit=1, **params)
        if models:
            return models[0]

    @classmethod
    def find(cls, id, **params):
        return cls.get(id, **params)


class UpdateMixin:
    """
    Exposes methods to update models on the Benchling server.
    """

    UPDATE_SCHEMA = "NOT IMPLEMENTED"

    @classmethod
    def update_model(cls, model_id, data, **params):
        response = cls._patch(data, path_params=[model_id], **params)
        return cls.load(response)

    def _update_from_data(self, data):
        r = self.update_model(self.id, data)
        self._update_from_other(r)
        return self

    def update_json(self):
        return self.dump(**dict(self.UPDATE_SCHEMA))

    def update(self):
        data = self.update_json()
        return self._update_from_data(data)


class CreateMixin:
    """
    Exposes methods that create new models on the Benchling server.
    """

    CREATE_SCHEMA = "Not implemented"

    @classmethod
    def create_model(cls, data, **params):
        response = cls._post(data, **params)
        return cls.load(response)

    @classmethod
    def bulk_create(cls, model_data, **params):
        response = cls._post(model_data, action="bulk-create", **params)
        return cls.load_many(response)

    def _create_from_data(self, data):
        r = self.create_model(data)
        self._update_from_other(r)
        return self

    def save_json(self):
        data = self.dump(**self.CREATE_SCHEMA)
        return data

    # TODO: remove schema_dumper with marshmallow > 3
    def save(self):
        data = self.save_json()
        return self._create_from_data(data)


class ArchiveMixin:
    """
    Exposes archiving and unarchiving methods
    """

    class ARCHIVE_REASONS:
        ERROR = "Made in error"
        RETIRED = 'Retired'
        EXPENDED = "Expended"
        SHIPPED = "Shipped"
        CONTAMINATED = "Contaminated"
        EXPIRED = "Expired"
        MISSING = "Missing"
        OTHER = "Other"
        NOT_ARCHIVED = "NOT_ARCHIVED"
        _DEFAULT = OTHER
        _REASONS = [ERROR, RETIRED, EXPENDED, SHIPPED, CONTAMINATED, EXPIRED, MISSING, OTHER]


    @classmethod
    def archive_many(cls, model_ids, reason=ARCHIVE_REASONS._DEFAULT):
        if reason not in cls.ARCHIVE_REASONS._REASONS:
            raise Exception("Reason must be one of {}".format(cls.ARCHIVE_REASONS._REASONS))
        key = cls.camelize("id")
        return cls._post(action="archive", data={key: model_ids, 'reason': reason})

    @classmethod
    def unarchive_many(cls, model_ids):
        key = cls.camelize("id")
        return cls._post(action="unarchive", data={key: model_ids})

    def archive(self, reason=ARCHIVE_REASONS._DEFAULT):
        self.archive_many([self.id], reason)
        self.reload()
        return self

    def unarchive(self):
        self.unarchive_many([self.id])
        self.reload()
        return self

    @property
    def is_archived(self):
        if hasattr(self, 'archiveRecord') and self.archiveRecord is not None:
            return True
        return False

    @property
    def archive_reason(self):
        if self.is_archived:
            return self.archiveRecord['reason']


class EntityMixin(ArchiveMixin, GetMixin, ListMixin, CreateMixin, UpdateMixin):
    """
    Entity methods (includes get, list, create, update)
    """

    @classmethod
    def find_by_name(cls, name, **params):
        models = cls.list(name=name, **params)
        if models:
            return models[0]

    def batches(self):
        """Get an entities batches"""
        result = self.session.http.get(self._url_build("entities", self.id, "batches"))
        return ModelRegistry.get_model("Batch").load_many(result['batches'])

    @classmethod
    def list_archived(cls, reason=ArchiveMixin.ARCHIVE_REASONS.OTHER):
        return cls.list(archiveReason=reason)

    def add_alias(self, name):
        if name not in self.aliases:
            self.aliases.append(name)
        return self


class InventoryMixin():
    """
    Designates model as having a folderId
    """

    def move(self, folderId):
        self.folderId = folderId
        self.update()


class RegistryMixin():
    """
    Allows model to be registered and unregistered.
    """

    ENTITY_TYPE = "unknown"

    class NAMING_STRATEGY:

        NEW_IDS = "NEW_IDS"
        IDS_FROM_NAMES = "IDS_FROM_NAMES"
        DELETE_NAMES = "DELETE NAMES"
        SET_FROM_NAME_PARTS = "SET_FROM_NAME_PARTS"
        _DEFAULT = NEW_IDS
        _STRATEGIES = [NEW_IDS, IDS_FROM_NAMES, DELETE_NAMES, SET_FROM_NAME_PARTS]

    @property
    def registry(self):
        return self.session.Registry.get(self.registryId)

    @classmethod
    def _valid_schema(cls, schema):
        return schema['type'] == cls.ENTITY_TYPE

    @classmethod
    def valid_schemas(cls):
        valid = []
        for r in cls.session.Registry.list():
            valid += [(r, schema) for schema in r.entity_schemas if cls._valid_schema(schema)]
        return valid

    def print_valid_schemas(self):
        schemas = self.valid_schemas()
        for r, s in schemas:
            print("Registry {} id={} -- {}".format(r.name, r.id, s['name']))

    def set_schema(self, schema_name, registry_id=None, registry_name=None):
        schema = None
        valid_schemas = self.valid_schemas()
        if not valid_schemas:
            raise BenchlingAPIException("No valid schemas found.")
        for r, s in valid_schemas:
            if s['name'] == schema_name:
                schema = s

        if not schema:
            raise BenchlingAPIException("No schema \"{}\" found. Select from {}".format(
                schema_name,
                [s['name'] for r, s in self.valid_schemas()]
            ))
        self.new_registry_id = schema['registryId']
        self.schemaId = schema['id']
        self.update()

    def register(self, naming_strategy=NAMING_STRATEGY._DEFAULT):
        if not hasattr(self, 'new_registry_id'):
                raise BenchlingAPIException("No schema set. Please use '{}' to set a schema. You may use '{}' "
                                            "to look at available schemas.".format(self.set_schema.__name__,
                                                                                   self.print_valid_schemas.__name__))
        self.session.Registry.register(self.new_registry_id, [self.id], naming_strategy=naming_strategy)
        self.reload()
        return self

    def unregister(self, folder_id=None):
        if folder_id is None:
            folder_id = self.folderId
        self.registry.unregister(self.registryId, [self.id], folder_id)
        self.reload()
        return self

    # TODO: test this method
    def register_with_custom_id(self, id):
        name = self.name
        self.name = id
        self.update()
        try:
            self.register(naming_strategy=self.NAMING_STRATEGY.IDS_FROM_NAMES)
        except BenchlingException as e:
            raise e
        finally:
            self.name = name
            self.update()
        return self

    # TODO: test this method
    def register_and_save_name_as_alias(self):
        self.register(naming_strategy=self.NAMING_STRATEGY.DELETE_NAMES)
        if self.name not in self.aliases:
            self.add_alias(self.name)
            self.update()
        return self

    @property
    def is_registered(self):
        if hasattr(self, 'registryId') and self.registryId is not None:
            if hasattr(self, 'new_registry_id'):
                if self.new_registry_id != self.registryId:
                    return False
            return True
        return False

    @classmethod
    def list_in_registry(cls, registry_id=None, registry_name=None, **params):
        if registry_id is None:
            registry_id = cls.session.Registry.find_registry(id=registry_id, name=registry_name).id
        return cls.list(registryId=registry_id, **params)

    @classmethod
    def registry_dict(cls, registry_id=None, registry_name=None, **params):
        entities = cls.list_in_registry(registry_id=registry_id, registry_name=registry_name, **params)
        return {e.entityRegistryId: e for e in entities}

    @classmethod
    def find_by_name_in_registry(cls, name, registry_id=None, registry_name=None, **params):
        models = cls.list_in_registry(registry_id=registry_id, registry_name=registry_name, name=name, **params)
        if models:
            return models[0]

    @classmethod
    def get_in_registry(cls, entity_registry_ids, registry_id=None, registry_name=None):
        registry = cls.session.Registry.find_registry(id=registry_id, name=registry_name)
        entity_data = registry.get_entities(entity_registry_ids)
        return cls.load_many(entity_data)

    @classmethod
    def find_in_registry(cls, entity_registry_id, registry_id=None, registry_name=None):
        entities = cls.get_in_registry([entity_registry_id], registry_id=registry_id, registry_name=registry_name)
        if entities:
            return entities[0]
        return None

    def unregister(self, folderId):
        registry = self.registry
        if registry is None:
            return
        registry.unregister_entities([self.id], folderId)
        self.reload()
        return self


class InventoryEntityMixin(InventoryMixin, RegistryMixin, EntityMixin):
    """
    Mixin for :class:`DNASequence`, :class:`AASequence`, and :class:`CustomEntity`
    """
    pass