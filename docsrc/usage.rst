Usage
=====

Installation
------------

.. code-block:: python

    pip install benchlingapi -U

Session
-------

Using the api requires an *api key*. If you do not have one,
you must request one from Benchling.

.. code-block:: python

    from benchlingapi import Session

    session = Session("sdf44tj-sdflj8na-rf23rfasdf")

From there, you can access various models:

.. code-block:: python

    session.DNASequence
    session.AASequence
    session.Oligo
    session.Folder
    session.Project
    session.Registry
    session.Translation
    session.EntitySchema
    session.Batch
    session.CustomEntity
    session.DNAAlignment
    session.Task


Have a look at the :ref:`API model docs <api_models>`
for methods available for each model.

Finding models
^^^^^^^^^^^^^^

.. code-block:: python

    # get one model
    dna = session.DNASequence.one()

    # find a specific model by its id
    dna = session.DNASequence.find('sdg_4tg23')

    # get the last 50 amino acids
    proteins = session.AASequence.last(50)

    # get a registry by name
    registry = session.Registry.find_by_name("Klavins Lab Registry")



Updating models
^^^^^^^^^^^^^^^

.. code-block:: python

    dna = session.DNASequence.one()
    dna.name = "My new name"
    dna.bases = "AGGTAGGGTAGGGCCAGAGA"

    # update the sequence on the server
    dna.update()


Saving new models
^^^^^^^^^^^^^^^^^

.. code-block:: python

    folder = session.Folder.find_by_name("My API Folder")
    dna = session.DNASequence(
        name = 'my new dna',
        bases = 'AGGTAGGATGGCCA',
        folder_id = folder.id,
        is_circular = False
    )

    # save the dna to your Benchling account
    dna.save()


Registering models to your registry
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    dna.set_schema("My DNA Schema")
    dna.register()


Submitting DNA Alignments
^^^^^^^^^^^^^^^^^^^^^^^^^'

.. code-block:: python

    task = session.DNAAlignment.submit_alignment(
        algorithm='mafft',
        name='my sequence alignment',
        filepaths=[
            'data/13dfg34.ab1'              # filepath to ab1 files
        ],
        sequences=[
            'seq_1erv452',              # a benchling sequence id
            session.DNASequence.one(),  # ...or a DNASequence instance
        ],
        rawfiles=None                       # only use if you have base64 data handy
    )

    # wait until the alignment is finished
    task.wait()

    # print the alignment
    print(task.response)

    # or grab the alignment
    alignment = task.response_class

    # from there, you can delete the alignment
    alignment.delete()

