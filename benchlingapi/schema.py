from marshmallow import Schema, post_load, SchemaOpts, validate
from marshmallow import fields as mfields
from benchlingapi.models import DNASequence, AASequence
from benchlingapi.base import ModelRegistry
# class DefaultFieldOptions(SchemaOpts):
#
#     allow_none = True
#     load_all = True


class ModelSchemaMixin(object):
    """Loads model from the Schema name"""

    @classmethod
    def get_model_name(cls):
        return cls.__name__.split("Schema")[0]

    # @classmethod
    # def get_model(cls):
    #     model = ModelRegistry.get_model(cls.get_model_name())
    #     return model

    @post_load
    def load_model(self, data):
        if "session" not in self.context:
            raise Exception("Schema does not have a Session instance attached!")
        session = self.context["session"]
        return session.interface(self.get_model_name())(**data)


class EntitySchema(Schema):
    entityRegistryId = mfields.String(allow_none=True)
    registryId = mfields.String(allow_none=True)
    archiveRecord = mfields.Dict(allow_none=True)
    id = mfields.String()
    name = mfields.String(required=True)
    createdAt = mfields.DateTime(load_only=True)
    modifiedAt = mfields.DateTime(load_only=True)
    creator = mfields.Dict()
    customfields = mfields.Dict()
    fields = mfields.Dict()
    schemaId = mfields.String()
    # schema = mfields.Dict(allow_none=True)
    # schema
    # entity
    # archiveRecord
    # mfields
    # custommfields
    webURL = mfields.URL()

    class Meta:
        additional = ("id",)


class CustomEntity(EntitySchema):
    aliases = mfields.List(mfields.String())
    folderId = mfields.String(required=True)


class SequenceSchema(EntitySchema, ModelSchemaMixin):
    aliases = mfields.List(mfields.String())
    folderId = mfields.String(required=True)
    length = mfields.Integer()


class DNASequenceSchema(SequenceSchema):

    annotations = mfields.Nested("AnnotationSchema", many=True)
    bases = mfields.String(required=True)
    isCircular = mfields.Boolean(required=True)
    translations = mfields.Nested("TranslationSchema", many=True)
    customFields = mfields.Raw()


class AASequenceSchema(SequenceSchema):

    annotations = mfields.Nested("AnnotationSchema", many=True)
    aminoAcids = mfields.String(required=True)


class OligoSchema(SequenceSchema):

    bases = mfields.String(required=True)


class BatchSchema(EntitySchema):

    pass


class AnnotationSchema(Schema, ModelSchemaMixin):
    color = mfields.String()
    start = mfields.Integer()
    end = mfields.Integer()
    name = mfields.String()
    strand = mfields.Integer(validate=validate.OneOf([0, 1, -1]))
    type = mfields.String()


class TranslationSchema(Schema):

    start = mfields.Integer()
    end = mfields.Integer()
    strand = mfields.Integer(validate=validate.OneOf([0, 1, -1]))
    aminoAcids = mfields.String()
    regions = mfields.List(mfields.Dict())


####################################
# Common Resources
####################################

class ArchiveRecordSchema(Schema):
    reason = mfields.String()


class UserSummarySchema(Schema):

    handle = mfields.String()
    id = mfields.String()
    name = mfields.String(allow_none=True)

####################################
# Projects and Folders
####################################


class FolderSchema(Schema, ModelSchemaMixin):
    id = mfields.String()
    name = mfields.String(required=True)
    parentFolderId = mfields.String(allow_none=True)
    projectId = mfields.String(required=True)
    archiveRecord = mfields.Nested(ArchiveRecordSchema, allow_none=True)

class ProjectSchema(Schema, ModelSchemaMixin):
    id = mfields.String()
    name = mfields.String()
    owner = mfields.Nested(UserSummarySchema)
    archiveRecord = mfields.Nested(ArchiveRecordSchema, allow_none=True)


