import base64
import os
import re
import time
import urllib
from typing import List
from typing import Type
from typing import Union

from benchlingapi.exceptions import BenchlingAPIException
from benchlingapi.models.base import ModelBase
from benchlingapi.models.base import ModelRegistry
from benchlingapi.models.mixins import ArchiveMixin
from benchlingapi.models.mixins import CreateMixin
from benchlingapi.models.mixins import DeleteMixin
from benchlingapi.models.mixins import EntityMixin
from benchlingapi.models.mixins import GetMixin
from benchlingapi.models.mixins import InventoryEntityMixin
from benchlingapi.models.mixins import InventoryMixin
from benchlingapi.models.mixins import ListMixin
from benchlingapi.models.mixins import RegistryMixin

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
    "EntitySchema",
    "DNAAlignment",
    "Task",
]


class CustomEntity(InventoryEntityMixin, ModelBase):
    """A Benchling CustomEntity model."""

    ENTITY_TYPE = "custom_entity"

    CREATE_SCHEMA = dict(
        only=("aliases", "custom_fields", "folder_id", "name", "schema_id")
    )

    UPDATE_SCHEMA = dict(
        only=("aliases", "custom_fields", "folder_id", "name", "schema_id")
    )

    def __init__(
        self,
        aliases=None,
        custom_fields=None,
        fields=None,
        folder_id=None,
        name=None,
        schema_id=None,
        schema=None,
        **kwargs
    ):
        self.aliases = aliases
        self.custom_fields = custom_fields
        self.fields = fields
        self.folder_id = folder_id
        self.name = name
        self.schema = schema
        self.schema_id = schema_id
        super().__init__(**kwargs)


class DNASequence(InventoryEntityMixin, ModelBase):
    """A model representing Benchling's DNASequence."""

    ENTITY_TYPE = "dna_sequence"

    CREATE_SCHEMA = dict(
        only=(
            "aliases",
            "annotations",
            "bases",
            "custom_fields",
            "fields",
            "folder_id",
            "is_circular",
            "name",
            "schema_id",
            "translations",
        )
    )

    UPDATE_SCHEMA = dict(
        only=(
            "aliases",
            "annotations",
            "bases",
            "custom_fields",
            "fields",
            "folder_id",
            "is_circular",
            "name",
            "schema_id",
            "translations",
            "primers",
        )
    )

    def __init__(
        self,
        aliases=None,
        annotations=None,
        bases=None,
        custom_fields=None,
        fields=None,
        folder_id=None,
        is_circular=None,
        name=None,
        schema_id=None,
        schema=None,
        translations=None,
        registry_id=None,
        **kwargs
    ):
        """Initialize.

        :param aliases:
        :param annotations:
        :param bases:
        :param custom_fields:
        :param fields:
        :param folder_id:
        :param is_circular:
        :param name:
        :param schema_id:
        :param schema:
        :param translations:
        :param kwargs:
        """
        self.aliases = aliases
        self.annotations = annotations
        self.bases = bases
        self.custom_fields = custom_fields
        self.fields = fields
        self.folder_id = folder_id
        self.is_circular = is_circular
        self.name = name
        self.translations = translations
        self.schema_id = schema_id
        self.schema = schema
        self.registry_id = registry_id
        super().__init__(**kwargs)

    @staticmethod
    def _opensharelink(share_link):
        """Hacky way to read the contents of a Benchling share link.

        :param share_link:
        :return:
        """
        # self._verifysharelink(share_link)
        f = urllib.request.urlopen(share_link)
        return f.read().decode("utf-8")

    @staticmethod
    def _parseURL(url):
        """A really hacky way to parse the Benchling api. This may become
        unstable.

        :param url:
        :return:
        """

        seq_pattern = r"seq[-_](?P<seq_id>\w+)-(?P<seq_name>[a-zA-Z0-9-_]+)"
        lib_pattern = r"lib[-_](?P<folder_id>\w+)-(?P<folder_name>[a-zA-Z0-9-_]+)"
        d = {}
        m1 = re.search(seq_pattern, url)
        m2 = re.search(lib_pattern, url)

        if m1:
            d.update(m1.groupdict())
            d["seq_id"] = "seq_" + d["seq_id"]
        if m2:
            d.update(m2.groupdict())
            d["folder_id"] = "lib_" + d["folder_id"]
        return d

    @classmethod
    def get_seq_id_from_link(cls, share_link: str):
        parsed = cls._parseURL(share_link)
        seq_id = parsed.get("seq_id", None)
        if seq_id:
            return seq_id
        else:
            try:
                text = cls._opensharelink(share_link)
                search_pattern = r"seq_\w+"
                possible_ids = re.findall(search_pattern, text)
                if len(possible_ids) == 0:
                    raise BenchlingAPIException(
                        "No sequence ids found in sharelink html using search pattern {}".format(
                            search_pattern
                        )
                    )
                uniq_ids = list(set(possible_ids))
                if len(uniq_ids) > 1:
                    raise BenchlingAPIException(
                        "More than one possible sequence id found in sharelink html using"
                        " search "
                        "pattern {}".format(search_pattern)
                    )
                seq_id = uniq_ids[0]
                return seq_id
            except (BenchlingAPIException, urllib.error.HTTPError):
                raise BenchlingAPIException(
                    "Could not find seqid in sharelink body or url."
                )

    @classmethod
    def from_share_link(cls, share_link):
        """Return a DNASequence based on its weblink.

        Weblink may be a share link or a url
        """
        return cls.get(cls.get_seq_id_from_link(share_link))

    @classmethod
    def list(
        cls,
        page_size: int = None,
        next_token: str = None,
        sort: str = None,
        archive_reason: str = None,
        folder_id: str = None,
        modified_at: str = None,
        name: str = None,
        project_id: str = None,
        schema_id: str = None,
        registry_id: str = None,
        **kwargs
    ):
        """List :class:`DNASequence` models.

        :param page_size: Number of results to return. Defaults to 50, maximum of 100.
        :param next_token: Token for pagination
        :param sort: Method by which to order search results. Valid sorts are
                    modifiedAt (modified time, most recent first) and name
                    (entity name, alphabetical). Optionally add :asc or
                    :desc to specify ascending or descending order.
                    Default is modifiedAt.
        :param archive_reason: Archive reason. Restricts DNA Sequences to those with
                the specified archive reason. Use “NOT_ARCHIVED” to filter for
                unarchived DNA Sequences.
        :param folder_id: ID of a folder. Restricts results to those in the folder.
        :param modified_at: Datetime, in RFC 3339 format. Supports the > and <
                    operators. Time zone defaults to UTC. Restricts results to those
                    modified in the specified range. e.g. > 2017-04-30.
        :param name: Name of a DNA Sequence. Restricts results to those with the
                    specified name.
        :param project_id: ID of a project. Restricts results to those in the project.
        :param schema_id: ID of a schema. Restricts results to those of the specified
                schema.
        :param registry_id: ID of a registry. Restricts results to those registered in
                this registry.
        :return:
        """
        return super().list(
            page_size=page_size,
            next_token=next_token,
            sort=sort,
            modified_at=modified_at,
            name=name,
            folder_id=folder_id,
            project_id=project_id,
            schema_id=schema_id,
            archive_reason=archive_reason,
            registry_id=registry_id,
            **kwargs
        )


class Task(GetMixin, ModelBase):
    """A model representing a long running task. Use `wait()` to wait for the
    results from the server. Use `reload()` to update the task from the server.

    .. versionadded:: 2.1.3
        Added :class:`DNASequence <benchlingapi.models.DNAAlignment>`
         model and corresponding
         :class:`Task <benchlingapi.models.Task>` and
         :class:`TaskSchema <benchlingapi.schema.TaskSchema>`.
    """

    def __init__(self, expected_class: Type[ModelBase] = None, **kwargs):
        self.expected_class = expected_class
        self.response_class = None
        self.response = None
        self.status = None
        self.message = None
        self.errors = None
        self.id = None
        super().__init__(**kwargs)

    def reload(self):
        ec = self.expected_class
        super().reload()
        self.expected_class = ec
        if hasattr(self, "response") and self.response and ec:
            self.response_class = ec.load(self.response)
        return self

    @classmethod
    def find(cls, id, **params):
        inst = super().find(id, **params)
        inst.id = id
        return inst

    def __repr__(self):
        return "<Task {}>".format(self.dump())

    def __str__(self):
        return self.__repr__()

    def wait(self, every_seconds: int = 3, timeout: int = 30):
        """Wait for the Task to finish.

        .. versionadded:: 2.1.2
            Added Task and TaskSchema models and the `wait()` method.

        :param every_seconds: time interval to check server
        :param timeout: maximum timeout in seconds
        :return: self
        """
        t1 = time.time()
        while self.status == "RUNNING":
            t2 = time.time()
            if t2 - t1 > timeout:
                raise TimeoutError(
                    "Task {} took too long ({}s)".format(self.id, timeout)
                )
            self.reload()
            time.sleep(every_seconds)
        return self


class DNAAlignment(GetMixin, DeleteMixin, ModelBase):
    """Represent a DNASequence alignment.

    .. versionadded:: 2.1.3
        Added :class:`DNASequence <benchlingapi.models.DNAAlignment>`
         model and corresponding
         :class:`Task <benchlingapi.models.Task>` and
         :class:`TaskSchema <benchlingapi.schema.TaskSchema>`.
    """

    MAFFT = "mafft"
    CLUSTALO = "clustalo"

    @staticmethod
    def model_to_id(seq):
        if isinstance(seq, str):
            return seq
        else:
            return seq.id

    @classmethod
    def _resolve_files(cls, sequences, filepaths, rawfiles):
        files_list = []
        if sequences:
            for seq in sequences:
                f = cls.model_to_id(seq)
                files_list.append({"sequenceId": cls.model_to_id(seq)})

        if filepaths:
            for filepath in filepaths:
                with open(filepath, "rb") as f:
                    b64data = base64.b64encode(f.read()).decode("utf-8")
                    files_list.append(
                        {"name": os.path.basename(filepath), "data": b64data}
                    )

        if rawfiles:
            for raw in rawfiles:
                files_list.append(raw)
        return files_list

    @classmethod
    def submit_alignment(
        cls,
        algorithm: str,
        name: str,
        template: Union[str, DNASequence],
        filepaths: List[str] = None,
        sequences: List[Union[str, DNASequence]] = None,
        rawfiles: List[str] = None,
    ) -> Task:
        """Submit an sequence alignment task.

        Usage:

        .. code-block:: python

            task = session.DNAAlignment.submit_alignment(
                algorithm='mafft',
                name='my sequence alignment',
                template='seq_yi2kdf2',         # the sequence id of the template
                filepaths=[
                    'data/13dfg34.ab1'          # filepath to ab1 files
                ],
                sequences=[
                    'seq_1erv452',              # a benchling sequence id
                    session.DNASequence.one(),  # ...or a DNASequence instance
                ],
                rawfiles=None                   # only use if you have base64 data handy
            )

            # wait until the alignment is finished
            task.wait()

            # print the alignment
            print(task.response)

            # or grab the alignment
            alignment = task.response_class

            # from there, you can delete the alignment
            alignment.delete()


        :param algorithm: either 'mafft' or 'clustalo'
        :param name: name of the sequence alignment
        :param template: template of the alignment. Either a benchling sequence id (str)
            or a :class:`DNASequence` instance containing a id.
        :param filepaths: optional list of sequencing filepaths to align to the template.
            For example, a list of .ab1 file paths.
        :param sequences: optional list of :class:`DNASequence` instances or benchling
            sequence ids to align to the template sequence.
        :param rawfiles: optional list of raw entries to send to align to the template.
            Use this if you have base64 bytes encoded data. Take a look at Benchling
            V2 API for more information.
        :return: Task
        """

        post_data = {
            "name": name,
            "algorithm": algorithm,
            "templateSequenceId": cls.model_to_id(template),
            "files": cls._resolve_files(sequences, filepaths, rawfiles),
        }

        if not post_data["files"]:
            raise BenchlingAPIException("No sequences or filepaths provided.")

        result = cls.session.http.post(
            "dna-alignments", action="create-template-alignment", json=post_data
        )

        inst = cls.session.Task.find(result["taskId"])
        inst.expected_class = cls
        return inst

    @classmethod
    def create_consensus(
        cls,
        algorithm: str,
        name: str,
        template: Union[str, DNASequence],
        consensus_sequence: Union[str, DNASequence],
        filepaths: List[str] = None,
        sequences: List[Union[str, DNASequence]] = None,
        rawfiles: List[str] = None,
    ):
        """Create a consensus sequence and save the sequence to the Benchling
        Server.

        .. versionadded:: 2.1.3
            Added `create_consensus`


        .. code-block:: python

            task = session.DNAAlignment.create_consensus(
                algorithm='mafft',
                name='my sequence alignment',
                filepaths=[
                    'data/13dfg34.ab1'          # filepath to ab1 files
                ],
                sequences=[
                    'seq_1erv452',              # a benchling sequence id
                    session.DNASequence.one(),  # ...or a DNASequence instance
                ],
                consensus_sequence=session.DNASequence(
                    folder_id="lib_23gv4r2",
                    name="my consensus",
                )
                rawfiles=None                   # only use if you have base64 data handy
            )

            # wait until the alignment is finished
            task.wait()

            # print the alignment
            print(task.response)

        :param algorithm: either 'mafft' or 'clustalo'
        :param name: name of the sequence alignment
        :param template: template of the alignment. Either a benchling sequence id (str)
            or a :class:`DNASequence` instance containing a id.
        :param consensus_sequence: either a DNASequence object (with folder_id) or
            a sequence id to save the consensus sequence.
        :param filepaths: optional list of sequencing filepaths to align to the template.
            For example, a list of .ab1 file paths.
        :param sequences: optional list of :class:`DNASequence` instances or benchling
            sequence ids to align to the template sequence.
        :param rawfiles: optional list of raw entries to send to align to the template.
            Use this if you have base64 bytes encoded data. Take a look at Benchling
            V2 API for more information.
        :return: Task
        """

        post_data = {
            "name": name,
            "algorithm": algorithm,
            "templateSequenceId": cls.model_to_id(template),
            "files": cls._resolve_files(sequences, filepaths, rawfiles),
        }

        if isinstance(consensus_sequence, str):
            post_data["sequenceId"] = consensus_sequence
        else:
            post_data["newSequence"] = consensus_sequence.dump()

        if not post_data["files"]:
            raise BenchlingAPIException("No sequences or filepaths provided.")

        result = cls.session.http.post(
            "dna-alignments", action="create-consensus-alignment", json=post_data
        )

        inst = cls.session.Task.find(result["taskId"])
        return inst


class AASequence(ModelBase, InventoryEntityMixin):
    """A model representing Benchling's AASequence (protein)."""

    ENTITY_TYPE = "aa_sequence"
    alias = "Protein"

    CREATE_SCHEMA = dict(
        only=(
            "aliases",
            "amino_acids",
            "custom_fields",
            "fields",
            "folder_id",
            "name",
            "schema_id",
        )
    )

    UPDATE_SCHEMA = dict(
        only=(
            "aliases",
            # "amino_aids",
            "custom_fields",
            "fields",
            "folder_id",
            "name",
            "schema_id",
        )
    )

    def __init__(
        self,
        aliases=None,
        amino_acids=None,
        custom_fields=None,
        fields=None,
        folder_id=None,
        name=None,
        schema_id=None,
        schema=None,
        **kwargs
    ):
        self.aliases = aliases
        self.amino_acids = amino_acids
        self.custom_fields = custom_fields
        self.fields = fields
        self.folder_id = folder_id
        self.name = name
        self.schema = schema
        self.schema_id = schema_id
        super().__init__(**kwargs)

    @classmethod
    def list(
        cls,
        page_size: int = None,
        next_token: str = None,
        sort: str = None,
        amino_acids: str = None,
        archive_reason: str = None,
        folder_id: str = None,
        modified_at: str = None,
        name: str = None,
        project_id: str = None,
        schema_id: str = None,
        registry_id: str = None,
        **kwargs
    ):
        """List :class:`AASequence` models.

        :param page_size: Number of results to return. Defaults to 50, maximum of 100.
        :param next_token: Token for pagination
        :param sort: Method by which to order search results. Valid sorts are modifiedAt
                (modified time, most recent first) and name (entity name, alphabetical).
                 Optionally add :asc or :desc to specify ascending or descending order.
                 Default is modifiedAt.
        :param archive_reason: Archive reason. Restricts DNA Sequences to those with the
                specified archive reason. Use “NOT_ARCHIVED” to filter for unarchived
                DNA Sequences.
        :param folder_id: ID of a folder. Restricts results to those in the folder.
        :param modified_at: Datetime, in RFC 3339 format. Supports the > and <
                operators. Time zone defaults to UTC. Restricts results to those
                modified in the specified range. e.g. > 2017-04-30.
        :param name: Name of a DNA Sequence. Restricts results to those with the
                specified name.
        :param project_id: ID of a project. Restricts results to those in the project.
        :param schema_id: ID of a schema. Restricts results to those of the specified
                schema.
        :param registry_id: ID of a registry. Restricts results to those registered in
                this registry.
        :return:
        """
        return super().list(
            page_size=page_size,
            next_token=next_token,
            sort=sort,
            amino_acids=amino_acids,
            modified_at=modified_at,
            name=name,
            folder_id=folder_id,
            project_id=project_id,
            schema_id=schema_id,
            archive_reason=archive_reason,
            registry_id=registry_id,
            **kwargs
        )


class Batch(RegistryMixin, EntityMixin, ModelBase):
    """A model representing a Batch."""

    CREATE_SCHEMA = dict(only=("entity_id", "fields"))

    UPDATE_SCHEMA = dict(only=("fields"))

    def __init__(self, entity_id=None, fields=None, **kwargs):
        self.entity_id = entity_id
        self.fields = fields
        super().__init__(**kwargs)


class Annotation(ModelBase):
    """A model representing a sequence Annotation."""

    pass


class Translation(ModelBase):
    """A model representing a protein translation."""

    pass


class Oligo(GetMixin, CreateMixin, InventoryMixin, RegistryMixin, ModelBase):
    """A model representing an Oligo."""

    CREATE_SCHEMA = dict(
        only=(
            "aliases",
            "bases",
            "custom_fields",
            "fields",
            "folder_id",
            "name",
            "schema_id",
        )
    )

    def __init__(
        self,
        aliases=None,
        bases=None,
        custom_fields=None,
        fields=None,
        folder_id=None,
        name=None,
        schema_id=None,
        schema=None,
        **kwargs
    ):
        self.aliases = aliases
        self.bases = bases
        self.custom_fields = custom_fields
        self.fields = fields
        self.folder_id = folder_id
        self.name = name
        self.schema_id = schema_id
        self.schema = schema
        super().__init__(**kwargs)


class Folder(GetMixin, ListMixin, ArchiveMixin, ModelBase):
    """A model representing a Benchling Folder."""

    def all_entities(self):
        """Generator that retrieves all entities in the folder."""
        entity_models = ModelRegistry.filter_models_by_base_classes(
            InventoryEntityMixin
        )
        for model in entity_models:

            interface = self.session.interface(model.__name__)
            for m in interface.all(folder_id=self.id):
                yield m


class Project(ListMixin, ArchiveMixin, ModelBase):
    """A model representing a Benchling Project."""


class EntitySchema(ModelBase):
    """A model representing an EntitySchema."""

    pass


class Registry(ListMixin, ModelBase):
    """A model representing a Benchling Registry."""

    @classmethod
    def get(cls, id):
        """Get registry by id."""
        for r in cls.list():
            if r.id == id:
                return r

    @classmethod
    def find_registry(cls, id: str = None, name: str = None) -> "Registry":
        """Finds a registry based on either id or name.

        If neither is provided and there is only 1 registry, return the
        only registry.
        """
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
        """List schemas."""
        data = self._get([self.id, "entity-schemas"])["entitySchemas"]
        return EntitySchema.load_many(data)

    def get_schema(self, name: str = None, id: str = None):
        """Get the schema of the registry.

        :param name: name of the registry
        :param id: id of the registry
        :return:
        """
        for schema in self.entity_schemas:
            if id:
                if schema["id"] == id:
                    return schema
            elif name:
                if schema["name"] == name:
                    return schema

    @classmethod
    def find_from_schema_id(cls, schema_id):
        """Find registry from a schema id."""
        for r in cls.list():
            for schema in r.entity_schemas:
                if schema["id"] == schema_id:
                    return r

    @classmethod
    def register(
        cls,
        registry_id: str,
        entity_ids: List[str],
        naming_strategy: str = RegistryMixin.NAMING_STRATEGY.DEFAULT,
    ):

        data = {"entity_ids": entity_ids, "naming_strategy": naming_strategy}
        return cls._post(data, path_params=[registry_id], action="register-entities")

    @classmethod
    def unregister(cls, registry_id, entity_ids, folder_id):
        data = {"entity_ids": entity_ids, "folder_id": folder_id}
        return cls._post(data, path_params=[registry_id], action="unregister-entities")

    def register_entities(self, entity_ids: List[str], naming_strategy: str = None):
        """Register entities by their ids."""
        return self.register(self.id, entity_ids, naming_strategy=naming_strategy)

    def unregister_entities(self, entity_ids, folder_id):
        """Unregister entities by their ids and move them to a new folder."""
        return self.unregister(self.id, entity_ids, folder_id)

    def get_entities(self, entity_registry_ids: List[str]) -> List["Registry"]:
        """Get entities by their ids."""
        return self._get(
            [self.id, "registered-entities"],
            action="bulk-get",
            params={"entity_registry_ids": entity_registry_ids},
        )["entities"]

    def find_in_registry(self, entity_registry_id) -> ModelBase:
        """Find entity by its id."""
        models = self.get_entities([entity_registry_id])
        if models:
            return models[0]


# class Annotation(ModelBase):
#
#     pass

# class UserSummary(ModelBase):
#
#     pass
