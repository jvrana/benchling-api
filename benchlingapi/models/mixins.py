"""Exposes models to various API endpoints."""
import webbrowser
from typing import Any
from typing import Callable
from typing import Generator
from typing import List
from typing import Tuple
from typing import Union

from benchlingapi.exceptions import BenchlingAPIException
from benchlingapi.exceptions import BenchlingServerException
from benchlingapi.models.base import ModelBase
from benchlingapi.models.base import ModelBaseABC
from benchlingapi.models.base import ModelRegistry


class GetMixin(ModelBaseABC):
    """Exposes the `get` and `find` by id methods."""

    @classmethod
    def get(cls, id: str, **params) -> ModelBase:
        """Get model by id (see 'find')"""
        try:
            response = cls._get(id, params=params)
        except BenchlingAPIException as e:
            if e.response.status_code == 404:
                return None
            raise e
        return cls.load(response)

    @classmethod
    def find(cls, id, **params) -> ModelBase:
        """Find model by id (see 'get')"""
        return cls.get(id, **params)


class ListMixin(ModelBaseABC):
    """Exposes the methods that return many model instances (e.g. `all`,
    `list`, `one`, etc.)"""

    MAX_PAGE_SIZE = 100

    @classmethod
    def list(cls, limit=None, **params) -> List[ModelBase]:
        """List models.

        :param params: extra parameters
        :return: list of models
        """
        if limit:
            return cls.all(limit=limit, **params)
        response = cls._get(params=params)
        return cls.load_many(response[cls._camelize()])

    @classmethod
    def list_pages(
        cls, page_limit: int = None, **params
    ) -> Generator[List[ModelBase], None, None]:
        """Return a generator pages of models.

        :param page_limit: return page limit
        :param params: extra parameters
        :return: generator of list of models
        """
        generator = cls._get_pages(params=params)
        response = next(generator, None)
        page_num = 1
        while response is not None and (page_limit is None or page_num <= page_limit):
            yield cls.load_many(response[cls._camelize()])
            response = next(generator, None)
            page_num += 1

    @classmethod
    def all(
        cls, page_limit: int = None, limit: int = None, **params
    ) -> Generator[ModelBase, None, None]:
        """Return a generator comprising of all models.

        :param page_limit: return page limit
        :param limit: number of model to return
        :param params: extra parameters
        :return: generator of models
        """
        num = 0
        for page in cls.list_pages(page_limit=page_limit, **params):
            for m in page:
                yield m
                num += 1
                if limit is not None and num >= limit:
                    return

    @classmethod
    def last(cls, num: int = 1, **params) -> List[ModelBase]:
        """Returns the most recent models.

        :param num: number of models to return
        :type num: int
        :param params: additional search parameters
        :type params: dict
        :return: list of models
        """
        max_page_size = min(
            cls.MAX_PAGE_SIZE, params.get("pageSize", cls.MAX_PAGE_SIZE)
        )
        if num <= max_page_size:
            max_page_size = num
        return list(cls.all(pageSize=max_page_size, limit=num))

    @classmethod
    def first(cls, num: int = 1, **params) -> List[ModelBase]:
        """Returns the most recent models.

        :param num: number of models to return
        :param params: additional search parameters
        :return: list of models
        """
        max_page_size = min(
            cls.MAX_PAGE_SIZE, params.get("pageSize", cls.MAX_PAGE_SIZE)
        )
        if num <= max_page_size:
            max_page_size = num
        return list(cls.all(pageSize=max_page_size, limit=num))

    @classmethod
    def one(cls, **params) -> ModelBase:
        """Returns one model."""
        models = cls.last(1, **params)
        if models:
            return models[0]

    @classmethod
    def search(
        cls, fxn: Callable, limit: int = 1, page_limit: int = 5, **params
    ) -> List[ModelBase]:
        """Search all models such that 'fxn' is True.

        :param fxn: function to return model
        :param limit: number of models to return (default 1)
        :param page_limit: number of pages to iterate (default 5)
        :param params: additional search parameters
        :return: list of models where 'fxn(model)' is True
        """
        found = []
        for model in cls.all(page_limit=page_limit, **params):
            if fxn(model):
                found.append(model)
            if len(found) >= limit:
                return found
        return found

    @classmethod
    def find_by_name(cls, name: str, page_limit=5, **params) -> ModelBase:
        """Find a model by name.

        :param name: the model name
        :param page_limit: the return page limit
        :param params: extra parameters
        :return: the model
        """
        models = cls.search(
            lambda x: x.name == name, limit=1, page_limit=page_limit, **params
        )
        if models:
            return models[0]

    @classmethod
    def get(cls, id: str, **params) -> ModelBase:
        """Get a single model by its id.

        :param id: the model id
        :param params: extra parameters
        :return: the model
        """
        models = cls.search(lambda x: x.id == id, limit=1, **params)
        if models:
            return models[0]

    @classmethod
    def find(cls, id, **params):
        """Get a single model by its id. See :method:`get`

        :param id: the model id
        :param params: extra parameters
        :return: the model
        """
        return cls.get(id, **params)


class UpdateMixin(ModelBaseABC):
    """Exposes methods to update models on the Benchling server."""

    UPDATE_SCHEMA = "NOT IMPLEMENTED"

    @classmethod
    def update_model(cls, model_id: str, data: dict, **params) -> ModelBase:
        """Update the model with data."""
        response = cls._patch(data, path_params=[model_id], **params)
        return cls.load(response)

    def _update_from_data(self, data: dict) -> ModelBase:
        r = self.update_model(self.id, data)
        self._update_from_other(r)
        return self

    def update_json(self) -> dict:
        """return the update json for the model instance."""
        return self.dump(**dict(self.UPDATE_SCHEMA))

    def update(self) -> ModelBase:
        """Update the model instance."""
        if not self.id:
            raise BenchlingAPIException("Cannot update. Model has not yet been saved.")
        data = self.update_json()
        return self._update_from_data(data)


class CreateMixin(ModelBaseABC):
    """Exposes methods that create new models on the Benchling server."""

    CREATE_SCHEMA = "Not implemented"

    @classmethod
    def create_model(cls, data: dict, **params) -> ModelBase:
        """Create model from data."""
        response = cls._post(data, **params)
        return cls.load(response)

    @classmethod
    def bulk_create(cls, model_data: dict, **params) -> List[ModelBase]:
        """Create many models from a list of data."""
        response = cls._post(model_data, action="bulk-create", **params)
        return cls.load_many(response)

    def _create_from_data(self, data) -> ModelBase:
        r = self.create_model(data)
        self._update_from_other(r)
        return self

    def save_json(self) -> dict:
        """Return the save json for this model instance."""
        data = self.dump(**self.CREATE_SCHEMA)
        return data

    # TODO: remove schema_dumper with marshmallow > 3
    def save(self) -> ModelBase:
        """Save this model to Benchling."""
        data = self.save_json()
        return self._create_from_data(data)


class ArchiveMixin(ModelBaseABC):
    """Exposes archiving and unarchiving methods."""

    class ARCHIVE_REASONS:
        """Reasons for archival."""

        ERROR = "Made in error"
        RETIRED = "Retired"
        EXPENDED = "Expended"
        SHIPPED = "Shipped"
        CONTAMINATED = "Contaminated"
        EXPIRED = "Expired"
        MISSING = "Missing"
        OTHER = "Other"
        NOT_ARCHIVED = "NOT_ARCHIVED"
        DEFAULT = OTHER
        REASONS = [
            ERROR,
            RETIRED,
            EXPENDED,
            SHIPPED,
            CONTAMINATED,
            EXPIRED,
            MISSING,
            OTHER,
        ]

    @classmethod
    def archive_many(cls, model_ids: List[str], reason=ARCHIVE_REASONS.DEFAULT) -> Any:
        """Archive many models by their ids.

        :param model_ids: list of ids
        :param reason: reason for archival (default "Other"). Select from
                        `model.ARCHIVE_REASONS`
        :return: list of models archived
        """
        if reason not in cls.ARCHIVE_REASONS.REASONS:
            raise Exception(
                "Reason must be one of {}".format(cls.ARCHIVE_REASONS.REASONS)
            )
        key = cls._camelize("id")
        return cls._post(action="archive", data={key: model_ids, "reason": reason})

    @classmethod
    def unarchive_many(cls, model_ids: List[str]) -> Any:
        """Unarchive many models by their ids.

        :param model_ids: list of ids
                :return: list of models unarchived
        """
        key = cls._camelize("id")
        return cls._post(action="unarchive", data={key: model_ids})

    def archive(self, reason=ARCHIVE_REASONS.DEFAULT) -> ModelBase:
        """Archive model instance.

        :param reason: reason for archival (default "Other"). Select from
                        `model.ARCHIVE_REASONS`
                :return:
        :rtype:
        """
        self.archive_many([self.id], reason)
        self.reload()
        return self

    def unarchive(self) -> ModelBase:
        """Unarchive the model instance.

        :return: model instance
        """
        self.unarchive_many([self.id])
        self.reload()
        return self

    @property
    def is_archived(self) -> bool:
        """Check whether model instance is archived."""
        if hasattr(self, "archive_record") and self.archive_record is not None:
            return True
        return False

    @property
    def archive_reason(self) -> str:
        """Return the archive reason.

        Return None if not archived.
        """
        if self.is_archived:
            return self.archive_record["reason"]


class EntityMixin(ArchiveMixin, GetMixin, ListMixin, CreateMixin, UpdateMixin):
    """Entity methods (includes get, list, create, update)"""

    DEFAULT_MERGE_FIELDS = set()

    @classmethod
    def find_by_name(cls, name: str, **params) -> ModelBase:
        """Find entity by name."""
        models = cls.list(name=name, **params)
        if models:
            return models[0]

    def batches(self) -> ModelBase:
        """Get an entities batches."""
        result = self.session.http.get(self._url_build("entities", self.id, "batches"))
        return ModelRegistry.get_model("Batch").load_many(result["batches"])

    @classmethod
    def list_archived(
        cls, reason: str = ArchiveMixin.ARCHIVE_REASONS.OTHER
    ) -> List[ModelBase]:
        """List archived entities."""
        return cls.list(archiveReason=reason)

    def add_alias(self, name: str) -> ModelBase:
        """Add an alias to the entity."""
        if name not in self.aliases:
            self.aliases.append(name)
        return self

    def open(self, key="webURL"):
        if hasattr(self, key):
            webbrowser.open(getattr(self, key))

    def update_json(self):
        data = super().update_json()
        if "fields" in data:
            data["fields"] = {
                k: {"value": v["value"]} for k, v in data["fields"].items()
            }
        return data

    def merge(self, on: dict = None) -> ModelBase:
        """
        Provided with a list of fields to search, merge the model
        with an existing model on the server (if it exists), else creates a new model.

        If no models found using
        the fields, a new model is created. If more than one model found,
        an exception is raised. If one model is found, that model is updated
        with the data from this model.

        .. versionadded: 2.1.4

        :param on: list of fields to search the server.
        :return: the model
        """
        if hasattr(self, "DEFAULT_MERGE_FIELDS") and on is None:
            on = self.DEFAULT_MERGE_FIELDS
        if not on:
            raise BenchlingAPIException(
                "Cannot merge. Must specify fields" " to merge with"
            )

        params = {}
        for key in on:
            if hasattr(self, key):
                params[key] = getattr(self, key)
            else:
                raise BenchlingAPIException(
                    "Cannot merge. Model is missing {} attribute".format(key)
                )
        models = self.list(**params)

        if len(models) == 1:
            self.id = models[0].id
            self.update()
            return self
        elif len(models) == 0:
            self.save()
            return self
        else:
            raise BenchlingAPIException(
                "Cannot merge. More than one"
                " {} found with merge fields {}".format(self.__class__.__name__, on)
            )


class InventoryMixin(ModelBaseABC):
    """Designates model as having a folderId."""

    def move(self, folder_id: str) -> ModelBase:
        """Move the entity to a new benchling folder.

        :param folder_id: the folder id to move entity to
                :return: model instance
        """
        self.folder_id = folder_id
        self.update()
        return self


class RegistryMixin(ModelBaseABC):
    """Mixin that allows entities to be registered or unregistered."""

    ENTITY_TYPE = "unknown"

    class NAMING_STRATEGY:
        """Naming strategy."""

        NEW_IDS = "NEW_IDS"
        IDS_FROM_NAMES = "IDS_FROM_NAMES"
        DELETE_NAMES = "DELETE NAMES"
        SET_FROM_NAME_PARTS = "SET_FROM_NAME_PARTS"
        DEFAULT = NEW_IDS
        STRATEGIES = [NEW_IDS, IDS_FROM_NAMES, DELETE_NAMES, SET_FROM_NAME_PARTS]

    @property
    def registry(self) -> ModelBase:
        """Return the :class:`models.Registry` that this entity is contained
        in."""
        return self.session.Registry.get(self.registry_id)

    @classmethod
    def _valid_schema(cls, schema) -> bool:
        return schema["type"] == cls.ENTITY_TYPE

    @classmethod
    def valid_schemas(cls):
        """Return valid schemas for this model class."""
        valid = []
        for r in cls.session.Registry.list():
            valid += [
                (r, schema) for schema in r.entity_schemas if cls._valid_schema(schema)
            ]
        return valid

    def print_valid_schemas(self):
        """Print available valid schemas for this model instance."""
        schemas = self.valid_schemas()
        for r, s in schemas:
            print("Registry {} id={} -- {}".format(r.name, r.id, s["name"]))

    def set_schema(self, schema_name):
        """Set the schema for this model instance."""
        schema = None
        valid_schemas = self.valid_schemas()
        if not valid_schemas:
            raise BenchlingAPIException("No valid schemas found.")
        for r, s in valid_schemas:
            if s["name"] == schema_name:
                schema = s

        if not schema:
            raise BenchlingAPIException(
                'No schema "{}" found. Select from {}'.format(
                    schema_name, [s["name"] for r, s in self.valid_schemas()]
                )
            )
        self.new_registry_id = schema["registry_id"]
        self.schema_id = schema["id"]
        self.update()

    def register(self, naming_strategy=NAMING_STRATEGY.DEFAULT):
        """Register this instance.

        :param naming_strategy: naming strategy for registry.
            - NEW_IDS (default): Generates new registry IDs, and leaves entity name
                as-is
            - IDS_FROM_NAMES: Converts names into registry IDs
            - DELETE_NAMES: Generates new registry IDs and sets entity name to
                new registry ID, and does not keep old names as aliases
            - SET_FROM_NAME_PARTS: Generates new registry IDs and generates
                new entity name based on the entity schema's name template, if it has
                one.
                :return: model instance
        """
        if not hasattr(self, "new_registry_id"):
            raise BenchlingAPIException(
                "No schema set. Please use '{}' to set a schema. You may use '{}' "
                "to look at available schemas.".format(
                    self.set_schema.__name__, self.print_valid_schemas.__name__
                )
            )
        self.session.Registry.register(
            self.new_registry_id, [self.id], naming_strategy=naming_strategy
        )
        self.reload()
        return self

    def unregister(self, folder_id=None):
        """Unregister the instance.

        :param folder_id: folder to move unregistered instance to
                :return: instance
        """
        if folder_id is None:
            folder_id = self.folder_id
        self.registry.unregister(self.registry_id, [self.id], folder_id)
        self.reload()
        return self

    # TODO: test this method
    def register_with_custom_id(self, id):
        """Register the instance with a custom id.

        :param id: custom registry id for the newly registered instance
                :return: instance
        """
        name = self.name
        self.name = id
        self.update()
        try:
            self.register(naming_strategy=self.NAMING_STRATEGY.IDS_FROM_NAMES)
        except BenchlingServerException as e:
            raise e
        finally:
            self.name = name
            self.update()
        return self

    # TODO: test this method
    def register_and_save_name_as_alias(self):
        """Register the instance, automatically generating a new id and setting
        the instance name to the new id. Save the old name as an alias.

        :return: instance
        """
        self.register(naming_strategy=self.NAMING_STRATEGY.DELETE_NAMES)
        if self.name not in self.aliases:
            self.add_alias(self.name)
            self.update()
        return self

    @property
    def is_registered(self):
        """Check if instance is registered."""
        if hasattr(self, "registry_id") and self.registry_id is not None:
            if hasattr(self, "new_registry_id"):
                if self.new_registry_id != self.registry_id:
                    return False
            return True
        return False

    @classmethod
    def list_in_registry(
        cls, registry_id: str = None, registry_name: str = None, **params
    ):
        """List instances contained in the registry.

        :param registry_id: registery id. If none, 'registry_name' must be provided.
                :param registry_name: registry name. If None, 'registry_id' must be provided
                :param params: additional search parameters
                :return: list of models in registry
        """
        if registry_id is None:
            registry_id = cls.session.Registry.find_registry(
                id=registry_id, name=registry_name
            ).id
        return cls.list(registry_id=registry_id, **params)

    @classmethod
    def all_in_registry(
        cls,
        registry_id: str = None,
        registry_name: str = None,
        limit: int = None,
        **params
    ):
        if registry_id is None:
            registry_id = cls.session.Registry.find_registry(
                id=registry_id, name=registry_name
            ).id
        return cls.all(registry_id=registry_id, limit=limit, **params)

    @classmethod
    def registry_dict(cls, registry_id=None, registry_name=None, **params):
        """Return a dictionary of registry ids to entities.

        :param registry_id: registery id. If none, 'registry_name' must be provided.
                :param registry_name: registry name. If None, 'registry_id' must be provided
                :param params: additional search parameters
                :return: dict of models in registry
        """
        entities = cls.list_in_registry(
            registry_id=registry_id, registry_name=registry_name, **params
        )
        return {e.entity_registry_id: e for e in entities}

    @classmethod
    def find_by_name_in_registry(
        cls, name: str, registry_id: str = None, registry_name: str = None, **params
    ) -> ModelBase:
        """Find entity by name in a registry.

        :param name: name of entity
        :param registry_id: registery id. If none, 'registry_name' must be provided.
        :param registry_name: registry name. If None, 'registry_id' must be provided
        :param params: additional search parameters
        :return: first model found
        """
        models = cls.list_in_registry(
            registry_id=registry_id, registry_name=registry_name, name=name, **params
        )
        if models:
            return models[0]

    @classmethod
    def get_in_registry(
        cls,
        entity_registry_ids: List[str],
        registry_id: str = None,
        registry_name: str = None,
    ) -> List[ModelBase]:
        """Get entities from a registry by their ids.

        :param entity_registry_ids: list of entity registry ids
        :param registry_id: registery id. If none, 'registry_name' must be provided.
        :param registry_name: registry name. If None, 'registry_id' must be provided
        :return: list of models in registry
        """
        registry = cls.session.Registry.find_registry(
            id=registry_id, name=registry_name
        )
        entity_data = registry.get_entities(entity_registry_ids)
        return cls.load_many(entity_data)

    @classmethod
    def find_in_registry(
        cls, entity_registry_id: str, registry_id: str = None, registry_name: str = None
    ):
        """Get an entity from a registry by their ids.

        :param entity_registry_id: entity registry id
        :param registry_id: registery id. If none, 'registry_name' must be provided.
        :param registry_name: registry name. If None, 'registry_id' must be provided
        :return: instance
        """
        entities = cls.get_in_registry(
            [entity_registry_id], registry_id=registry_id, registry_name=registry_name
        )
        if entities:
            return entities[0]
        return None


class InventoryEntityMixin(InventoryMixin, RegistryMixin, EntityMixin):
    """Mixin for :class:`DNASequence`, :class:`AASequence`, and.

    :class:`CustomEntity`
    """

    pass


class DeleteMixin(ModelBaseABC):
    def delete(self):
        return self._delete(path_params=[self.id])
