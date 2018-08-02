# BenchlingPyAPI

## Getting Started

### Installation

```
pip3 install benchlingapi -U
```

### Creating new session
You'll need a BenchlingAPI key...
```python
from benchlingapi import Session

session = Session('api_key_128795879dfkshdf')
```

### Available Models

Models can be accessed by `session.[ModelName]` such as `session.DNASequenc`

List of models can be printed using `print(session.models)`

#### Models:

`DNASequence` - a DNA sequence

`AASequence` - a protein

`Oligo` - a primer

`Project`

`Folder`

... more to come?


### Model Methods

`find` - find model by id
```python
seq = session.DNASequence.find('seq-324jl5')
```

`find_by_name` - iterates through models to find the first DNA sequence with the given name
```python
seq = session.DNASequence.find_by_name("puc19-GFP")
```

```python
# narrow down the search to a particular project
project = session.Project.find_by_name("MyProject")
seq = session.DNASequence.find_by_name("puc19-GFP", projectId=project.id)
```

`list` - list all models

```python
seqs = session.DNASequence.list()
```

`list_pages` - return paginated list of models

```python
for seqs in session.DNASequence.list_pages():
    print(seq)
```

`update` - updates model to Benchling

```python
folder = session.Folder.find_by_name('MyFolder')
folder.name = "My New Name"
folder.update()
```

`save` - saves a new model to Benchling

```python
# find folder
folder = session.Folder.find_by_name("Primers", projectId=session.Project.find_by_name("API_Folder").id)

# create some annotations
annotation1 = {
        "color": "#FF9CCD",
        "end": 3,
        "name": "bla gene",
        "start": 1,
        "strand": 1,
        "type": "gene"
}
annotation2 = {
        "color": "#FF9CCD",
        "end": 5,
        "name": "bla gene",
        "start": 1,
        "strand": -1,
        "type": "gene"
}

# make a new sequence
new_seq = session.DNASequence(
        bases="AGCGTATGTGTGTA",
        name="MyNewSeq",
        isCircular=False,
        annotations=[annotation1, annotation2],
        folderId=folder.id
)

# save it to benchling
new_seq.save()
```