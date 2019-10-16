# BenchlingAPI

The (unofficial) python API wrapper for Benchling.

## Installation

```
pip install benchlingapi -U
```

## Getting Started

`api = Session("your_secret_benchling_api_key")`

`api.DNASequence()`

`api.AASequence()`

`api.CustomEntity()`

`api.Oligo()`

`api.Registry.one()`

`api.DNASequence.one()`

`api.DNASequence.last(50)`

`api.Folder.find_by_name("MyFolderName")`

```
dna.set_schema("My DNA Schema")
dna.register()
```

## Features

### Models

stub

### Searching and Finding

stub

### Creation

stub

### Archiving/Unarchiving

stub

### Registering/Unregistering

stub

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