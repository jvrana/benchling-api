# benchlingapi
Python library for interacting with the Benchling web API

# Description
Benchling provides a convenient way to store DNA sequences (plasmids, primers, pcr
fragments, etc.) for an entire lab. However, accessing Benchling sequence information 
programmatically is a huge pain as Benchling's API is extremely limited. This 
project provides several convenience methods for accessing Benchling sequence 
information. The most useful feature is the ability to access Benchling sequences
from a sequence share-link.

Also included are more advanced features that integrate the DNA manipulation package Coral
and the aquarium-api-python package. From an Aquarium sample_id, this api can return
annotated sequences (as a Cor.DNA object) from a fragment or plasmid's benchling share-link.

Future Versions: Implement POST features. Unfortunately at the moment, I cannot get POST
requests to function properly in Benchling's API. This may be a limitation of their API.

# Installation

`cd directory/that/contains/setup.py`
`pip install .`

# Usage

## Importing
### Basic Features
    from benchlingapi import BenchlingAPI

### Advanced Features (requires Coral and AquariumAPI installed)
    from benchlingapi import BenchlingPortal

## Initializing the API object

### Basic Features
The BenchlingAPI object provides an interface for accessing Benchling sequences. 
It requires a benchling API-key, which can be requested from Benchling. More information
on the Benchling API can be accessed here: https://api.benchling.com/docs/.

	bench_api_key = 'sk_g7fo2vxkNUYNPkShOFIOmtY9ejIGE'
	benchlingapi = BenchlingAPI(bench_api_key)

The first argument is the Benchling API key, which can be requested through benchling and accessed by scrolling to the bottom of you account information on Benchling.

Note that initializing the BenchlingAPI object will take several seconds.

### Advanced Features (Coral and AquariumAPI integration)
For more advanced features, a subclass of the BenchlingAPI is provided as BenchlingPortal.
BenchlingPortal contains Coral and Aquarium integration features. Initializing the BenchlingPortal
object requires the benchling API key and Aquarium API login information.

	bench_api_key = 'sk_g7fo2vxkNUYNPkShOFIOmtY9ejIGE'
    aq_api_key = 'GwZdTb4jr8YL3wwmVi1QYfG6jeLzUYxkLSZ7BAIKnOc'
    aq_user = 'vrana'
    aq_url = 'http://54.68.9.194:81/api'
    benchlingportal = BenchlingPortal(bench_api_key, aq_api_key, aq_user, aq_url)

The first argument is the Benchling API key, which can be requested through benchling and accessed by scrolling to the bottom of you account information on Benchling.

The second argument is the URL of the api - this comes in the format of `"{base aquarium URL}/api"`. Make sure to use the testing server to validate your submissions if you're creating new samples/items/tasks!

The third argument is your aquarium username.

The fourth argument is your aquarium API key, which can be found by clicking Account&gt;Profile and generating a key

Note that initializing the BenchlingPortal object will take several seconds.

## Making requests

There are a few options for interacting with the the BenchlingAPI once the BenchlingAPI object
has been initialized:

1. Get sequence information from a Benchling Share link through BenchlingAPI or BenchlingPortal
2. Collect all benchling sequences information through BenchlingAPI or BenchlingPortal. This includes any sequences that may be shared with you on Benchling.
3. Collect all benchling folder information through BenchlingAPI or BenchlingPortal. This includes any folder that may be shared with you on Benchling.
4. Request an annotated Coral.DNA object from an Aquarium sample_id through BenchlingPortal


### 1. Getting Sequences from a Share Link
	credentials = [bench_api]
	api = BenchlingAPI(*credentials)
	seqs = api.getSequenceFromShareLink('https://benchling.com/s/k5Y05YM2/edit')


The method returns a dictionary that contains sequence information. The following is an example output:
{u'primers': [], u'description': u'', u'name': u'kanMX2', u'creator': u'ent_OMJVXnRI', u'color': u'#F7977A', u'created_at': u'2015-08-14T20:48:39.159409+00:00', u'tags': [{u'name': u'accession', u'value': u'S78175'}, {u'name': u'marker', u'value': u'KanR'}, {u'name': u'organism', u'value': u'Saccharomyces cerevisiae'}, {u'name': u'ref', u'value': u'pmid:7747518'}], u'modified_at': u'2015-08-14T20:48:39.489252+00:00', u'id': u'seq_6fEUBmhu', u'length': 1437, u'bases': u'GATATCAAGCTTGCCTCGTCCCCGCCGGGTCACCCGGCCAGCGACATGGAGGCCCAGAATACCCTCCTTGACAGTCTTGACGTGCGCAGCTCAGGGGCATGATGTGACTGTCGCCCGTACATTTAGCCCATACATCCCCATGTATAATCATTTGCATCCATACATTTTGATGGCCGCACGGCGCGAAGCAAAAATTACGGCTCCTCGCTGCAGACCTGCGAGCAGGGAAACGCTCCCCTCACAGACGCGTTGAATTGTCCCCACGCCGCGCCCCTGTAGAGAAATATAAAAGGTTAGGATTTGCCACTGAGGTTCTTCTTTCATATACTTCCTTTTAAAATCTTGCTAGGATACAGTTCTCACATCACATCCGAACATAAACAACCATGGGTAAGGAAAAGACTCACGTTTCGAGGCCGCGATTAAATTCCAACATGGATGCTGATTTATATGGGTATAAATGGGCTCGCGATAATGTCGGGCAATCAGGTGCGACAATCTATCGATTGTATGGGAAGCCCGATGCGCCAGAGTTGTTTCTGAAACATGGCAAAGGTAGCGTTGCCAATGATGTTACAGATGAGATGGTCAGACTAAACTGGCTGACGGAATTTATGCCTCTTCCGACCATCAAGCATTTTATCCGTACTCCTGATGATGCATGGTTACTCACCACTGCGATCCCCGGCAAAACAGCATTCCAGGTATTAGAAGAATATCCTGATTCAGGTGAAAATATTGTTGATGCGCTGGCAGTGTTCCTGCGCCGGTTGCATTCGATTCCTGTTTGTAATTGTCCTTTTAACAGCGATCGCGTATTTCGTCTCGCTCAGGCGCAATCACGAATGAATAACGGTTTGGTTGATGCGAGTGATTTTGATGACGAGCGTAATGGCTGGCCTGTTGAACAAGTCTGGAAAGAAATGCATAAGCTTTTGCCATTCTCACCGGATTCAGTCGTCACTCATGGTGATTTCTCACTTGATAACCTTATTTTTGACGAGGGGAAATTAATAGGTTGTATTGATGTTGGACGAGTCGGAATCGCAGACCGATACCAGGATCTTGCCATCCTATGGAACTGCCTCGGTGAGTTTTCTCCTTCATTACAGAAACGGCTTTTTCAAAAATATGGTATTGATAATCCTGATATGAATAAATTGCAGTTTCATTTGATGCTCGATGAGTTTTTCTAATCAGTACTGACAATAAAAAGATTCTTGTTTTCAAGAACTTGTCATTTGTATAGTTTTTTTATATTGTAGTTGTTCTATTTTAATCAAATGTTAGCGTGATTTATATTTTTTTTCGCCTCGACATCATCTGCCCAGATGCGAAGTTAAGTGCGCAGAAAGTAATATCATGCGTCAATCGTATGTGAATGCTGGTCGCTATACTGCTGTCGATTCGATACTAACGCCGCCATCCAGTGTCGAC', u'notes': [{u'text': u'kanMX selector module conferring kanamycin resistance, for gene disruption in yeast, kanMX2 version.', u'created_at': u'2015-08-14T20:48:39.159409+00:00', u'creator': u'ent_OMJVXnRI'}, {u'text': u'', u'created_at': u'2015-08-14T20:48:39.159409+00:00', u'creator': u'ent_OMJVXnRI'}, {u'text': u'<small>[1] New heterologous modules for classical or PCR-based gene disruptions in Saccharomyces cerevisiae. Yeast 1994;10:1793-808. Wach A, Brachat A, P\xf6hlmann R, Philippsen P. (pmid:7747518)</small>', u'created_at': u'2015-08-14T20:48:39.159409+00:00', u'creator': u'ent_OMJVXnRI'}], u'owner': u'ent_OMJVXnRI', u'folder': u'lib_l807ls2n', u'annotations': [{u'end': 386, u'name': u'TEF promoter', u'color': u'#C6C9D1', u'start': 42, u'type': u'promoter', u'strand': 1}, {u'end': 1399, u'name': u'TEF terminator', u'color': u'#C6C9D1', u'start': 1201, u'type': u'terminator', u'strand': 0}, {u'end': 1399, u'name': u'kanMX', u'color': u'#F58A5E', u'start': 42, u'type': u'gene', u'strand': 1}, {u'end': 1196, u'name': u'KanR', u'color': u'#B7E6D7', u'start': 386, u'type': u'CDS', u'strand': 1}], u'circular': False}

### 2. Getting all sequences
	credentials = [bench_api]
	api = BenchlingAPI(*credentials)
	seqs = api.getAllSequences()

This method returns a list of all benchling sequences (including those shared with you on Benchling).

### 3. Getting all folders
	credentials = [bench_api]
	api = BenchlingAPI(*credentials)
	seqs = api.getAllFolders()

This method returns a list of all folder information (including those shared with you on Benchling).
### 4. Request Coral.DNA from sample_id (requires Coral and AquariumAPI installed)
credentials = [bench_api, aq_url, aq_user, aq_api_key]
portal = BenchlingPortal(*credentials)

	coral_dna = portal.getSequenceFromAquarium(11231, query='id')

OR

	coral_dna = portal.getSequenceFromAquarium('pMOD4-pGPD-CTerminalDNASensor', query='name')
