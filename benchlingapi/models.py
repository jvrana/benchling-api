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
]


class ArchiveMixin(object):
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


class DNASequence(ModelBase, ArchiveMixin):

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
        return self.create_model(self.schema_dumper(self.save_schema(), self))

    # TODO: remove schema_dumper with marshmallow > 3
    def update(self):
        return self.update_model(self.id, self.schema_dumper(self.update_schema(), self))

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
class AASequence(ModelBase, ArchiveMixin):

    alias = "Protein"


class Annotation(ModelBase):

    pass


class Oligo(ModelBase):

    pass


class Translation(ModelBase):

    pass


class Folder(ModelBase, ArchiveMixin):

    pass

class Project(ModelBase, ArchiveMixin):

    pass


# class Annotation(ModelBase):
#
#     pass

# class UserSummary(ModelBase):
#
#     pass
