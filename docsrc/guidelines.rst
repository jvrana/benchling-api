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

To run pytests, some api credentials are needed. To run
tests, add a file `tests/secrets/config.json` containing, your
cretentials, an example sharelink, an example project,
an example trash_folder, and an example inventory_folder.

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