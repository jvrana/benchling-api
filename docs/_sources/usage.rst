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

You can access models from the session.
Have a look at the :ref:`API model docs <api_models>`
for methods available for each model.

.. code-block::

    seq = session.DNASequence.last(1)
    seq.register()
    print(seq.dump())


