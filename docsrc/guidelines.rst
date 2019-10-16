Contributing
============

Adding a new model
------------------

To implement a new model, please refer to the official
`Benchling documentation <https://docs.benchling.com/reference>`_. After,
review the docs, find the appropriate class
:mod:`mixins <benchlingapi.models.mixins>` to implement the new model and
inherit the :class:`ModelBase <benchlingapi.models.base.ModelBase>`
Finally, create a new :mod:`schema <benchlingapi.models.schema>`, to
implement the attributes the model will inherit from benchling
results, following the convention of using *under_score* attribute
names. Implement methods using the
`_post`, `_get`, `_get_pages`, `_patch` methods of
:class:`ModelBase <benchlingapi.models.base.ModelBase>` as needed.

Running tests
-------------

Testing is done using `pytest`. Tests will create live requests to a Benchling account.
Since testing is done live, a Benchling account will need to be setup along with testing
data.

.. code-block:: json

    {
      "credentials": {
        "api_key": "asdasdfadsfaghrhrha"
      },
      "sharelinks": [
        "https://benchling.com/s/seq-asdffebarha"
      ],
      "project": {
        "name": "API_sasdfs_iuAAXqsdfadsftuk"
      },
      "trash_folder": {
        "name": "API_Trash"
      },
      "inventory_folder": {
        "name": "API_Inventory"
      }
    }

On the Benchling side of things, in the account liked to the `credentials["api_key"]`, you must
have a project corresponding to the `project["name"]` value above. Within this project, you should
have two folder corresponding to the `trash_folder` and `inventory_folder` values above. Additionally,
you should have at least one example of an AminoAcid, DNASequence, CustomEntity, and Oligo stored within
your `inventory_folder`. Tests will copy the examples from the `inventory_folder` for downstream tests.
After the tests, conclude, inventory in the `trash_folder` will get archived.