"""
Model serialization/deserialization classes
"""

import re

from marshmallow import Schema, post_load, post_dump, validate
from marshmallow import fields as mfields


class ModelSchemaMixin(object):
    """Loads model from the Schema name"""

    @classmethod
    def get_model_name(cls):
        return re.match("(\w+)Schema", cls.__name__).group(1)

    # @classmethod
    # def get_model(cls):
    #     model = ModelRegistry.get_model(cls.get_model_name())
    #     return model

    # @pre_dump
    # def remove_none(self, obj):
    #     params = obj
    #     if hasattr(obj, '__dict__'):
    #         params = params.__dict__
    #     return {k: v for k, v in params.items() if v is not None}

    @post_dump
    def remove_ignore(self, data):
        return {k: v for k, v in data.items() if v is not None}

    @post_load
    def load_model(self, data):
        if "session" not in self.context:
            raise Exception("Schema does not have a Session instance attached!")
        session = self.context["session"]
        return session.interface(self.get_model_name())(**data)


class EntitySchema(Schema):
    entityRegistryId = mfields.String(default=None, allow_none=True)
    registryId = mfields.String(default=None, allow_none=True)
    archiveRecord = mfields.Dict(allow_none=True)
    id = mfields.String()
    name = mfields.String(required=True, allow_none=False)
    createdAt = mfields.DateTime(load_only=True)
    modifiedAt = mfields.DateTime(load_only=True)
    creator = mfields.Dict()
    customFields = mfields.Dict()
    fields = mfields.Dict(allow_none=False)
    schema = mfields.Nested("EntitySchemaSchema", allow_none=True)
    schemaId = mfields.Method('get_schema_id')
    aliases = mfields.List(mfields.String())
    folderId = mfields.String(required=True, allow_none=True)
    # schema = mfields.Dict(allow_none=True)
    # schema
    # entity
    # archiveRecord
    # mfields
    # custommfields
    webURL = mfields.URL()

    class Meta:
        additional = ("id",)

    def get_schema_id(self, obj):
        if hasattr(obj, 'schemaId') and obj.schemaId:
            return obj.schemaId
        elif hasattr(obj, 'schema') and obj.schema:
            return obj.schema['id']

class CustomEntitySchema(ModelSchemaMixin, EntitySchema):
    pass


class DNASequenceSchema(ModelSchemaMixin, EntitySchema):
    annotations = mfields.Nested("AnnotationSchema", many=True)
    length = mfields.Integer()
    bases = mfields.String(required=True)
    isCircular = mfields.Boolean(required=True)
    translations = mfields.Nested("TranslationSchema", many=True)


class AASequenceSchema(ModelSchemaMixin, EntitySchema):
    annotations = mfields.Nested("AnnotationSchema", many=True)
    aminoAcids = mfields.String(required=True)
    length = mfields.Integer()


class OligoSchema(ModelSchemaMixin, EntitySchema):
    bases = mfields.String(required=True)
    length = mfields.Integer()


class BatchSchema(EntitySchema):
    pass


class AnnotationSchema(ModelSchemaMixin, Schema):
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

# class ArchiveRecordSchema(Schema):
#     reason = mfields.String()


class FieldSchema(Schema):

    type = mfields.String(load_only=True)
    isMulti = mfields.Boolean(load_only=True)
    value = mfields.Raw()
    textValue = mfields.String(load_only=True)


class EntitySchemaSchema(Schema):
    archiveRecord = mfields.Dict(allow_none=True)
    id = mfields.String()
    name = mfields.String(required=True)
    type = mfields.String()
    fieldDefinitions = mfields.List(mfields.Dict)
    prefix = mfields.String()
    registryId = mfields.String(default=None, allow_none=True)
    constrain = mfields.Dict()


class UserSummarySchema(Schema):
    handle = mfields.String()
    id = mfields.String()
    name = mfields.String(allow_none=True)


####################################
# Projects and Folders
####################################


class FolderSchema(ModelSchemaMixin, Schema):
    id = mfields.String()
    name = mfields.String(required=True)
    parentFolderId = mfields.String(allow_none=True)
    projectId = mfields.String(required=True)
    archiveRecord = mfields.Dict(allow_none=True)


class ProjectSchema(ModelSchemaMixin, Schema):
    id = mfields.String()
    name = mfields.String()
    owner = mfields.Nested(UserSummarySchema)
    archiveRecord = mfields.Dict(allow_none=True)


class RegistrySchema(ModelSchemaMixin, Schema):
    id = mfields.String()
    name = mfields.String()
    owner = mfields.Nested(UserSummarySchema)
