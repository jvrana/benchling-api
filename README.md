# BenchlingAPI

[![PyPI version](https://badge.fury.io/py/benchlingapi.svg)](https://badge.fury.io/py/benchlingapi)

The (unofficial) python API wrapper for Benchling. For more information,
see documentation at https://klavinslab.github.io/benchling-api/index.

## Installation

```
pip install benchlingapi -U
```

## Getting Started

Initialize a session using your Benchling-provided API key:

```python
from benchlingapi import Session
session = Session("your_secret_benchling_api_key")
```

From there, you can access various models:

```python
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
```

Finding models:

```python
# get one model
dna = session.DNASequence.one()

# find a specific model by its id
dna = session.DNASequence.find('sdg_4tg23')

# get the last 50 amino acids
proteins = session.AASequence.last(50)

# get a registry by name
registry = session.Registry.find_by_name("Klavins Lab Registry")
```

Updating models:

```python
dna = session.DNASequence.one()
dna.name = "My new name"
dna.bases = "AGGTAGGGTAGGGCCAGAGA"

# update the sequence on the server
dna.update()
```

Saving new models:

```python
folder = session.Folder.find_by_name("My API Folder")
dna = session.DNASequence(
    name = 'my new dna',
    bases = 'AGGTAGGATGGCCA',
    folder_id = folder.id,
    is_circular = False
)

# save the dna to your Benchling account
dna.save()
```

Registering models to your registry:

```python
dna.set_schema("My DNA Schema")
dna.register()
```

See the documentation for more information: https://klavinslab.github.io/benchling-api/index

## Testing

Testing is done using `pytest`. Tests will create live requests to a Benchling account.
Since testing is done live, a Benchling account will need to be setup along with testing
data.

To run tests, you must have a Benchling Account with an API key. Tests require a file in
'tests/secrets/config.json' with the following format:

```
{
  "credentials": {
    "api_key": "asdahhjwrthsdfgadfadfgadadsfa"
  },
  "sharelinks": [
    "https://benchling.com/s/seq-asdfadsfaee"
  ],
  "project": {
    "name": "API"
  },
  "trash_folder": {
    "name": "API_Trash"
  },
  "inventory_folder": {
    "name": "API_Inventory"
  }
}
```

On the Benchling side of things, in the account liked to the `credentials["api_key"]`, you must
have a project corresponding to the `project["name"]` value above. Within this project, you should
have two folder corresponding to the `trash_folder` and `inventory_folder` values above. Additionally,
you should have at least one example of an AminoAcid, DNASequence, CustomEntity, and Oligo stored within
your `inventory_folder`. Tests will copy the examples from the `inventory_folder` for downstream tests.
After the tests, conclude, inventory in the `trash_folder` will get archived.

#### Happy Cloning!
