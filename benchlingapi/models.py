from benchlingapi.base import ModelBase
from benchlingapi.exceptions import BenchlingAPIException
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

__all__ = [
    "DNASequence",
    "AASequence",
    "Annotation",
    "Oligo",
    "Translation",
    "Folder",
    "Project",
    "EntitySchema",
    "Registry"
]


class ArchiveMixin():
    REASONS = ["Made in error", "Retired", "Expended", "Shipped", "Contaminated", "Expired", "Missing", "Other"]

    @classmethod
    def archive_many(cls, model_ids, reason):
        if reason not in cls.REASONS:
            raise Exception("Reason must be one of {}".format(cls.REASONS))
        key = cls.camelize("id")
        return cls._post(action="archive", data={key: model_ids, "reason": reason})

    @classmethod
    def unarchive_many(cls, model_ids):
        key = cls.camelize("id")
        return cls._post(action="archive", data={key: model_ids})

    def archive(self, reason):
        return self.archive_many([self.id])

    def unarchive(self, reason):
        return self.unarchive_many([self.id])


class RegisterMixin():

    def get_registry(self):
        return self.session.Registry.find(self.registryId)

    def set_schema(self, registry_id=None, registry_name=None, schema_name=None):
        if registry_id:
            registry = self.session.Registry.find(registry_id)
        elif registry_name:
            registry = self.session.Registry.find_by_name(registry_name)
        else:
            registry = self.get_registry()

        schema = registry.get_schema(name=schema_name)
        self.schema_id = schema['id']
        self.schema = schema
        self.update()

    def register(self, registry_id=None, registry_name=None, namingStrategy=None):
        if self.schemaId is None:
            raise BenchlingAPIException("Cannot register. Model must have a schema attached.")
        if registry_id:
            registry = self.session.Registry.find(registry_id)
        else:
            registry = self.session.Registry.find_by_name(registry_name)

        self.update()
        registry.registry_entities([self.id], namingStrategy)
        self.__dict__.update(self.session.DNASequence.find(self.id).__dict__)
        return self

    def unregister(self, folderId):
        registry = self.get_registry()
        if registry is None:
            return
        registry.unregister_entities([self.id], folderId)
        self.__dict__.update(self.session.DNASequence.find(self.id).__dict__)



class DNASequence(RegisterMixin, ArchiveMixin, ModelBase):

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
            "customFields",
            "fields",
            "folderId",
            "isCircular",
            "name",
            "schemaId",
        ))

    # TODO: remove schema_dumper with marshmallow > 3
    def save(self):
        data = self.schema_dumper(self.save_schema(), self)
        return self._create_from_data(data)

    # TODO: remove schema_dumper with marshmallow > 3
    def reload(self):
        seq = self.find(self.id)
        data = self.schema_dumper(seq.update_schema(), seq)
        self.__dict__.update(data)
        return self

    def update(self):
        data = self.schema_dumper(self.update_schema(), self)
        return self._update_from_data(data)

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
        seq = None
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
class AASequence(RegisterMixin, ArchiveMixin, ModelBase):

    alias = "Protein"


class Annotation(ModelBase):

    pass


class Oligo(ModelBase):

    pass


class Translation(ModelBase):

    pass


class Folder(ArchiveMixin, ModelBase):

    pass

class Project(ArchiveMixin, ModelBase):

    pass

class EntitySchema(ArchiveMixin, ModelBase):

    pass

class Registry(ModelBase):

    @classmethod
    def get(cls, id):
        for r in cls.list():
            if r.id == id:
                return r

    @classmethod
    def find_by_name(cls, name):
        registries = cls.list()
        for r in registries:
            if r.name == name:
                return r

    @property
    def entity_schemas(self):
        return self._get([self.id, 'entity-schemas'])['entitySchemas']

    def registry_entities(self, entity_ids, namingStrategy=None):
        """
        
        :param entity_ids: list of entity ids
        :type entity_ids: list
        :param namingStrategy: one of NEW_IDS, IDS_FROM_NAMES, DELETE_NAMES, SET_FROM_NAME_PARTS
        :type namingStrategy: 
        :return: 
        :rtype: 
        """
        naming_strategies = ["NEW_IDS", "IDS_FROM_NAMES", "DELETE_NAMES", "SET_FROM_NAME_PARTS"]
        if namingStrategy is None:
            namingStrategy = naming_strategies[0]

        data = {
            "entityIds": entity_ids,
            "namingStrategy": namingStrategy,
        }
        return self._post(data, path_params=[self.id], action="register-entities")

    def unregister_entities(self, entity_ids, folder_id):
        data = {
            'entityIds': entity_ids,
            'folderId': folder_id
        }
        return self._post(data, path_params=[self.id], action="unregister-entities")

    def get_schema(self, name=None, id=None):
        for schema in self.entity_schemas:
            if id:
                if schema['id'] == id:
                    return schema
            elif name:
                if schema['name'] == name:
                    return schema

# class Annotation(ModelBase):
#
#     pass

# class UserSummary(ModelBase):
#
#     pass
