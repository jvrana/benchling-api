import re
from urllib.request import urlopen

from benchlingapi.models.base import ModelBase
from benchlingapi.exceptions import BenchlingAPIException
from benchlingapi.models.mixins import GetMixin, ListMixin, ArchiveMixin, EntityMixin, RegistryMixin, CreateMixin, UpdateMixin

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

class CustomEntity(RegistryMixin, ModelBase):

    ENTITY_TYPE = "custom_entity"


class DNASequence(RegistryMixin, ModelBase):

    ENTITY_TYPE = "dna_sequence"

    def save_schema(self):
        return self.schema(only=(
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
        ))

    def update_schema(self):
        return self.schema(only=(
            "aliases",
            "bases",
            "customFields",
            "fields",
            "folderId",
            "isCircular",
            "name",
            "schemaId",
        ))

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
class AASequence(RegistryMixin, ModelBase):

    ENTITY_TYPE = "aa_sequence"
    alias = "Protein"

    def save_schema(self):
        return self.schema(only=(
            "aliases",
            "aminoAcids",
            "customFields",
            "fields",
            "folderId",
            "name",
            "schemaId",
        ))

    def update_schema(self):
        return self.schema(only=(
            "aliases",
            "aminoAcids",
            "customFields",
            "fields",
            "folderId",
            "name",
            "schemaId",
        ))


class Batch(EntityMixin, ModelBase):

    pass


class Annotation(ModelBase):
    pass


class Translation(ModelBase):
    pass



class Oligo(GetMixin, CreateMixin, ModelBase):

    ENTITY_TYPE = "sequence"


class Folder(GetMixin, ListMixin, ArchiveMixin, ModelBase):

    pass


class Project(ListMixin, ArchiveMixin, ModelBase):

    pass


class EntitySchema(ModelBase):

    pass


class Registry(ListMixin, ModelBase):

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

# class Annotation(ModelBase):
#
#     pass

# class UserSummary(ModelBase):
#
#     pass
