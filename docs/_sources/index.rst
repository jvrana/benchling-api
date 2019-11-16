:github_url: |homepage|


Python BenchlingAPI
===================

The unofficial Benchling API for Python. |homepage|

.. code-block::

    pip install benchlingapi -U

.. code-block:: python

    from benchlingapi import Session

    api_key = 'aksdj45ywe5yey5y'
    session = Session(api_key)
    seq = session.DNASequence.last()
    print(seq.dump())

API Reference
-------------

.. toctree::
   :maxdepth: 1

   session
   models
   exceptions
   utils


User Documentation
------------------

The user documentation contains high-level information for users.

.. toctree::
   :maxdepth: 1

   usage

Developer Documentation
-----------------------

The developer documentation conatins information on how to contribute..

.. toctree::
   :maxdepth: 1

   guidelines
   developer/changelog
