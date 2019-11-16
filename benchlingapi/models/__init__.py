r"""
Models (:mod:`benchlingapi.models.models`)
==========================================

This module contains the Benchling API models. Models
are accessed from a session instance as follows:

.. code-block:: python

    from benchlingapi import Session

    session = Session("asdfe8iunaoerhgoaher")
    session.DNASequence
    session.AASequence
    session.Oligo
    session.Registry
    # and so on

.. currentmodule:: benchlingapi.models.models

Models
------

.. autosummary::
    :toctree: generated/

    DNASequence
    AASequence
    Oligo
    Annotation
    Translation
    CustomEntity
    EntitySchema
    Project
    Registry
    Translation
    DNAAlignment
    Task

Schemas
-------

Schemas define how JSON data is consumed and produced from the Benchling server.

.. currentmodule:: benchlingapi.models.schema

.. autosummary::
    :toctree: generated/

    DNASequenceSchema
    AASequenceSchema
    BatchSchema
    CustomEntitySchema
    DNASequenceSchema
    EntitySchema
    EntitySchemaSchema
    FieldSchema
    FolderSchema
    OligoSchema
    ProjectSchema
    RegistrySchema
    TranslationSchema
    UserSummarySchema
    DNAAlignmentSchema
    TaskSchema
"""
from benchlingapi.models import schema
from benchlingapi.models.base import ModelRegistry
from benchlingapi.models.models import AASequence
from benchlingapi.models.models import Annotation
from benchlingapi.models.models import Batch
from benchlingapi.models.models import CustomEntity
from benchlingapi.models.models import DNAAlignment
from benchlingapi.models.models import DNASequence
from benchlingapi.models.models import EntitySchema
from benchlingapi.models.models import Folder
from benchlingapi.models.models import Oligo
from benchlingapi.models.models import Project
from benchlingapi.models.models import Registry
from benchlingapi.models.models import Task
from benchlingapi.models.models import Translation
