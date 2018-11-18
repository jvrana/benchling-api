"""
All BenchlingAPI models
"""

import re
from urllib.request import urlopen

from benchlingapi.exceptions import BenchlingAPIException
from benchlingapi.models.base import ModelBase, ModelRegistry
from benchlingapi.models.mixins import GetMixin, ListMixin, ArchiveMixin, EntityMixin, RegistryMixin, CreateMixin, \
    InventoryMixin, InventoryEntityMixin

__all__ = [
    "DNASequence",
    "AASequence",
    "Annotation",
    "Oligo",
    "Translation",
    "Folder",
    "Project",
    "CustomEntity",
    "Batch",
    "Registry",
    "EntitySchema"
]

# TODO: implement 'fields' for CustomEntity
class CustomEntity(InventoryEntityMixin, ModelBase):
    """
    A Benchling CustomEntity model.
    """

    ENTITY_TYPE = "custom_entity"

    CREATE_SCHEMA = dict(only=(
        "aliases",
        "customFields",
        "folderId",
        "name",
        "schemaId"
    )
    )

    UPDATE_SCHEMA = dict(only=("aliases", "customFields",
                               "folderId", "name", "schemaId"
                               )
                         )

    def __init__(self, aliases=None, customFields=None,
                 fields=None, folderId=None,
                 name=None, schemaId=None, schema=None, **kwargs):
        self.aliases = aliases
        self.customFields = customFields
        self.fields = fields
        self.folderId = folderId
        self.name = name
        self.schema = schema
        self.schemaId = schemaId
        super().__init__(**kwargs)


class DNASequence(InventoryEntityMixin, ModelBase):
    """
    A model representing Benchling's DNASequence.
    """

    ENTITY_TYPE = "dna_sequence"

    CREATE_SCHEMA = dict(
        only=(
            "aliases",
            "annotations",
            "bases",
            "customFields",
            "fields",
            "folderId",
            "isCircular",
            "name",
            "schemaId",
            "translations"
        )
    )

    UPDATE_SCHEMA = dict(
        only=(
            "aliases",
            "bases",
            "customFields",
            "fields",
            "folderId",
            "isCircular",
            "name",
            "schemaId",
        )
    )

    def __init__(self, aliases=None, annotations=None, bases=None, customFields=None,
                 fields=None, folderId=None, isCircular=None, name=None, schemaId=None,
                 schema=None,
                 translations=None, **kwargs):
        self.aliases = aliases
        self.annotations = annotations
        self.bases = bases
        self.customFields = customFields
        self.fields = fields
        self.folderId = folderId
        self.isCircular = isCircular
        self.name = name
        self.translations = translations
        self.schemaId = schemaId
        self.schema = schema
        super().__init__(**kwargs)

    @staticmethod
    def _opensharelink(share_link):
        """
        Hacky way to read the contents of a Benchling share link
        :param share_link:
        :return:
        """
        # self._verifysharelink(share_link)
        f = urlopen(share_link)
        return f.read().decode("utf-8")

    @staticmethod
    def _parseURL(url):
        """
        A really hacky way to parse the Benchling api. This may become unstable.
        :param url:
        :return:
        """
        g = re.search('benchling.com/(?P<user>\w+)/f/(?P<folderid>\w+)' + \
                      '-(?P<foldername>\w+)/seq-(?P<seqid>\w+)-(?P<seqname>' + \
                      '[a-zA-Z0-9_-]+)', url)
        labels = ['user', 'folder_id', 'folder_name', 'seq_id', 'seq_name']
        d = dict(list(zip(labels, g.groups())))
        d['seq_id'] = 'seq_{}'.format(d['seq_id'])
        return d

    @classmethod
    def from_share_link(cls, share_link):
        try:
            text = cls._opensharelink(share_link)
            search_pattern = "seq_\w+"
            possible_ids = re.findall(search_pattern, text)
            if len(possible_ids) == 0:
                raise BenchlingAPIException("No sequence ids found in sharelink html using search pattern {}".format(
                    search_pattern))
            uniq_ids = list(set(possible_ids))
            if len(uniq_ids) > 1:
                raise BenchlingAPIException("More than one possible sequence id found in sharelink html using search "
                                            "pattern {}".format(search_pattern))
            seq = uniq_ids[0]
        except BenchlingAPIException:
            d = cls._parseURL(share_link)
            seq = d['seq_id']
        if seq is None:
            raise BenchlingAPIException("Could not find seqid in sharelink body or url.")
        return cls.get(seq)


# TODO: use alias for parameters
class AASequence(InventoryEntityMixin, ModelBase):
    """
    A model representing Benchling's AASequence (protein).
    """

    ENTITY_TYPE = "aa_sequence"
    alias = "Protein"

    CREATE_SCHEMA = (
        dict(
            only=(
                "aliases",
                "aminoAcids",
                "customFields",
                "fields",
                "folderId",
                "name",
                "schemaId",
            )
        )
    )

    UPDATE_SCHEMA = (
        dict(
            only=(
                "aliases",
                "aminoAcids",
                "customFields",
                "fields",
                "folderId",
                "name",
                "schemaId",
            )
        )
    )

    def __init__(self, aliases=None, aminoAcids=None, customFields=None,
                 fields=None, folderId=None, name=None, schemaId=None,
                 schema=None,
                 **kwargs):
        self.aliases = aliases
        self.aminoAcids = aminoAcids
        self.customFields = customFields
        self.fields = fields
        self.folderId = folderId
        self.name = name
        self.schema = schema
        self.schemaId = schemaId
        super().__init__(**kwargs)


class Batch(RegistryMixin, EntityMixin, ModelBase):
    """
    A model representing a Batch.
    """

    CREATE_SCHEMA = dict(
        only=(
            'entityId',
            'fields'
        )
    )

    UPDATE_SCHEMA = dict(
        only=(
            'fields'
        )
    )

    def __init__(self, entityId=None, fields=None, **kwargs):
        self.entityId = entityId
        self.fields = fields
        super().__init__(**kwargs)


class Annotation(ModelBase):
    """
    A model representing a sequence Annotation.
    """
    pass


class Translation(ModelBase):
    """
    A model representing a protein translation.
    """
    pass

class Oligo(GetMixin, CreateMixin, InventoryMixin, RegistryMixin, ModelBase):
    """
    A model representing an Oligo.
    """

    CREATE_SCHEMA = dict(
        only=(
            "aliases",
            "bases",
            "customFields",
            "fields",
            "folderId",
            "name",
            "schemaId"
        )
    )

    def __init__(self, aliases=None, bases=None, customFields=None, fields=None,
                 folderId=None, name=None, schemaId=None, schema=None, **kwargs):
        self.aliases = aliases
        self.bases = bases
        self.customFields = customFields
        self.fields = fields
        self.folderId = folderId
        self.name = name
        self.schemaId = schemaId
        self.schema = schema
        super().__init__(**kwargs)


class Folder(GetMixin, ListMixin, ArchiveMixin, ModelBase):
    """
    A model representing a Benchling Folder.
    """

    def all_entities(self):
        """Generator that retrieves all entities in the folder."""
        entity_models = ModelRegistry.filter_models_by_base_classes(InventoryEntityMixin)
        for model in entity_models:

            interface = self.session.interface(model.__name__)
            for m in interface.all(folderId=self.id):
                yield m


class Project(ListMixin, ArchiveMixin, ModelBase):
    """
    A model representing a Benchling Project.
    """


class EntitySchema(ModelBase):
    """
    A model representing an EntitySchema.
    """
    pass


class Registry(ListMixin, ModelBase):
    """
    A model representing a Registry.
    """

    @classmethod
    def get(cls, id):
        for r in cls.list():
            if r.id == id:
                return r

    @classmethod
    def find_registry(cls, id=None, name=None):
        """Finds a registry based on either id or name. If neither is provided and there
        is only 1 registry, return the only registry."""
        if id:
            return cls.get(id)
        elif name:
            return cls.find_by_name(name)
        else:
            registries = cls.list()
            if len(registries) == 1:
                return registries[0]

    @property
    def entity_schemas(self):
        data = self._get([self.id, 'entity-schemas'])['entitySchemas']
        return EntitySchema.load_many(data)

    def get_schema(self, name=None, id=None):
        for schema in self.entity_schemas:
            if id:
                if schema['id'] == id:
                    return schema
            elif name:
                if schema['name'] == name:
                    return schema

    @classmethod
    def find_from_schema_id(cls, schema_id):
        for r in cls.list():
            for schema in r.entity_schemas:
                if schema['id'] == schema_id:
                    return r

    @classmethod
    def register(cls, registry_id, entity_ids, naming_strategy=RegistryMixin.NAMING_STRATEGY._DEFAULT):

        data = {
            "entityIds": entity_ids,
            "namingStrategy": naming_strategy,
        }
        return cls._post(data, path_params=[registry_id], action="register-entities")

    @classmethod
    def unregister(cls, registry_id, entity_ids, folder_id):
        data = {
            'entityIds': entity_ids,
            'folderId': folder_id
        }
        return cls._post(data, path_params=[registry_id], action="unregister-entities")

    def register_entities(self, entity_ids, naming_strategy=None):
        return self.register(self.id, entity_ids, naming_strategy=naming_strategy)

    def unregister_entities(self, entity_ids, folder_id):
        return self.unregister(self.id, entity_ids, folder_id)

    def get_entities(self, entity_registry_ids):
        return self._get([self.id, 'registered-entities'], action='bulk-get', params={
            'entityRegistryIds': entity_registry_ids
        })['entities']

    def find_in_registry(self, entity_registry_id):
        models = self.get_entities([entity_registry_id])
        if models:
            return models[0]

# class Annotation(ModelBase):
#
#     pass

# class UserSummary(ModelBase):
#
#     pass
