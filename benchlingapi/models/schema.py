"""Model serialization/deserialization classes."""
import re

from marshmallow import fields as mfields
from marshmallow import INCLUDE
from marshmallow import post_dump
from marshmallow import post_load
from marshmallow import Schema
from marshmallow import validate


class ModelSchemaMixin:
    """Loads model from the Schema name."""

    @classmethod
    def get_model_name(cls):
        return re.match(r"(\w+)Schema", cls.__name__).group(1)

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
    def remove_ignore(self, data, **kwargs):
        return {k: v for k, v in data.items() if v is not None}

    @post_load
    def load_model(self, data, **kwrags):
        if "session" not in self.context:
            raise Exception("Schema does not have a Session instance attached!")
        session = self.context["session"]
        return session.interface(self.get_model_name())(**data)


class EntitySchema(Schema):
    entity_registry_id = mfields.String(default=None, allow_none=True)
    registry_id = mfields.String(default=None, allow_none=True)
    archive_reason = mfields.Dict(allow_none=True)
    id = mfields.String()
    name = mfields.String(required=True, allow_none=False)
    created_at = mfields.String(load_only=True)
    modified_at = mfields.String(load_only=True)
    creator = mfields.Dict()
    custom_fields = mfields.Dict()
    fields = mfields.Dict(allow_none=False)
    schema = mfields.Nested("EntitySchemaSchema", allow_none=True)
    schema_id = mfields.Method("get_schema_id")
    aliases = mfields.List(mfields.String())
    folder_id = mfields.String(required=True, allow_none=True)
    # schema = mfields.Dict(allow_none=True)
    # schema
    # entity
    # archive_record
    # mfields
    # custommfields
    web_url = mfields.URL()

    class Meta:
        unknown = INCLUDE
        additional = ("id",)

    def get_schema_id(self, obj):
        if hasattr(obj, "schema_id") and obj.schema_id:
            return obj.schema_id
        elif hasattr(obj, "schema") and obj.schema:
            return obj.schema["id"]


class CustomEntitySchema(ModelSchemaMixin, EntitySchema):
    class Meta:
        unknown = INCLUDE


class OligoSchema(ModelSchemaMixin, EntitySchema):
    length = mfields.Integer()
    bases = mfields.String(required=True)

    class Meta:
        unknown = INCLUDE


class OligoBinding(Schema):
    bases = mfields.String()
    bind_position = mfields.Integer()
    color = mfields.String()
    start = mfields.Integer()
    end = mfields.Integer()
    name = mfields.String()
    overhang_length = mfields.Integer()
    strand = mfields.Integer()

    class Meta:
        unknown = INCLUDE


class DNASequenceSchema(ModelSchemaMixin, EntitySchema):
    annotations = mfields.Nested("AnnotationSchema", many=True)
    length = mfields.Integer()
    bases = mfields.String(required=True)
    is_circular = mfields.Boolean(required=True)
    translations = mfields.Nested("TranslationSchema", many=True)
    primers = mfields.Nested("OligoBinding", many=True)

    class Meta:
        unknown = INCLUDE


class AASequenceSchema(ModelSchemaMixin, EntitySchema):
    annotations = mfields.Nested("AnnotationSchema", many=True)
    amino_acids = mfields.String(required=True)
    length = mfields.Integer()

    class Meta:
        unknown = INCLUDE


class OligoSchema(ModelSchemaMixin, EntitySchema):
    bases = mfields.String(required=True)
    length = mfields.Integer()

    class Meta:
        unknown = INCLUDE


class BatchSchema(EntitySchema):

    entity_id = mfields.String()

    class Meta:
        unknown = INCLUDE


class AnnotationSchema(ModelSchemaMixin, Schema):
    color = mfields.String()
    start = mfields.Integer()
    end = mfields.Integer()
    name = mfields.String()
    strand = mfields.Integer(validate=validate.OneOf([0, 1, -1]))
    type = mfields.String()

    class Meta:
        unknown = INCLUDE


class TranslationSchema(Schema):
    start = mfields.Integer()
    end = mfields.Integer()
    strand = mfields.Integer(validate=validate.OneOf([0, 1, -1]))
    amino_acids = mfields.String()
    regions = mfields.List(mfields.Dict())

    class Meta:
        unknown = INCLUDE


# class DNAAlignmentEntrySchema(Schema):
#
#     bases = mfields.Str()
#     dna_sequence_id: mfields.Str()
#     trim_start = mfields.Int()
#     trim_end = mfields.Int()
#
#
class DNAAlignmentSchema(ModelSchemaMixin, Schema):

    aligned_sequences = mfields.List(mfields.Dict())
    name = mfields.Str()

    class Meta:
        unknown = INCLUDE


####################################
# Common Resources
####################################

# class ArchiveRecordSchema(Schema):
#     reason = mfields.String()


class FieldSchema(Schema):
    type = mfields.String(load_only=True)
    is_multi = mfields.Boolean(load_only=True)
    value = mfields.Raw()
    text_value = mfields.String(load_only=True, allow_none=True)

    class Meta:
        unknown = INCLUDE


class EntitySchemaSchema(Schema):
    archive_record = mfields.Dict(allow_none=True)
    id = mfields.String()
    name = mfields.String(required=True)
    type = mfields.String()
    field_definitions = mfields.List(mfields.Dict)
    prefix = mfields.String()
    registry_id = mfields.String(default=None, allow_none=True)
    constrain = mfields.Dict()

    class Meta:
        unknown = INCLUDE


class UserSummarySchema(Schema):
    handle = mfields.String()
    id = mfields.String()
    name = mfields.String(allow_none=True)

    class Meta:
        unknown = INCLUDE


class TaskSchema(ModelSchemaMixin, Schema):
    """Schema for :class:`Task <benchlingapi.models.Task>`

    .. versionadded:: 2.1.3
        Added :class:`DNASequence <benchlingapi.models.DNAAlignment>`
         model and corresponding
         :class:`Task <benchlingapi.models.Task>` and
         :class:`TaskSchema <benchlingapi.schema.TaskSchema>`.
    """

    status = mfields.Str()
    errors = mfields.List(mfields.Dict, allow_none=True, required=False)
    message = mfields.Str(allow_none=True, required=False)
    response = mfields.Dict(allow_none=True, required=False)
    id = mfields.Str()

    class Meta:
        unknown = INCLUDE


####################################
# Projects and Folders
####################################


class FolderSchema(ModelSchemaMixin, Schema):
    id = mfields.String()
    name = mfields.String(required=True)
    parent_folder_id = mfields.String(allow_none=True)
    project_id = mfields.String(required=True)
    archive_record = mfields.Dict(allow_none=True)

    class Meta:
        unknown = INCLUDE


class ProjectSchema(ModelSchemaMixin, Schema):
    id = mfields.String()  #: the id of the project
    name = mfields.String()  #: the name of the project
    owner = mfields.Nested(UserSummarySchema)  #: the owner of the project
    archive_record = mfields.Dict(allow_none=True)

    class Meta:
        unknown = INCLUDE


class RegistrySchema(ModelSchemaMixin, Schema):
    id = mfields.String()
    name = mfields.String()
    owner = mfields.Nested(UserSummarySchema)

    class Meta:
        unknown = INCLUDE
