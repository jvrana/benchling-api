
# Description
Benchling provides a convenient way to store DNA sequences (plasmids, primers, pcr
fragments, etc.) for an entire lab. However, accessing Benchling sequence information 
programmatically is a huge pain as Benchling's API is extremely limited. This 
project provides several convenience methods for accessing Benchling sequence 
information. A useful feature is the ability to access Benchling sequences
from a sequence share-link.

There is currently no Python3 support.

# Installation
	cd directory/that/contains/setup.py
	pip install .

# Usage

## Initializing the API object

### Basic Features
The BenchlingAPI object provides an interface for accessing Benchling sequences. 
It requires a benchling API-key, which can be requested from Benchling. More information
on the Benchling API can be accessed here: https://api.benchling.com/docs/.

	from benchlingapi import BenchlingAPI
	
	bench_api_key = 'sk_g7fo2vxkNUYNPkShOFIOmtY9ejIXX'
	benchlingapi = BenchlingAPI(bench_api_key)

The first argument is the Benchling API key, which can be requested through benchling and accessed by scrolling to the bottom of you account information on Benchling.

#### Find

e.g. find all sequences that contain the word "CRY2" in the name

	benchlingapi.findSequence('CRY2', query='name', regex=True)
	
e.g. find all sequences that with regular expression pattern

	benchlingapi.findSequence('\wcas9.+', query='name', regex=True)
	
e.g. find all sequence with id 'seq_aupKOZRb'

	benchlingapi.findSequence('seq_aupKOZRb', query='id', regex=False)
	
	
e.g. find all folders that contain the word "CRY2" in the name

	benchlingapi.findFolder('CRY2', query='name', regex=True)
	
e.g. get all folders

	benchlingapi.getFolderList()
	
e.g. get all sequences
	
	benchlingapi.getSequenceList()
	
e.g. get sequence from a share link

	benchlingapi.getSequenceFromShareLink('share_link')

#### Create

e.g. create a folder

	benchlingapi.createFolder('new_folder', description='this is a new folder', owner='ent_OMJXXX')

e.g. create a sequence

	benchlingapi.createSequence(
		'sequence name', #name
		'agggggggtctgtagctgacttatcgtatgtgcgcga', #bases
		True, #circular or not
		'lib_0g4T1FJV', #folder_id
		description='sequence description',
		#annotations=[], #annotations are not currently supported in Benchling's api
		)
		
e.g. create a folder

	benchlingapi.createFolder('folder_Name', description='folder_description', 'owner'='ent_OMJXXX')
	
#### Delete

e.g. delete a folder

	benchlingapi.deleteFolder(folder_id)

e.g. delete a sequence

	benchlingapi.deleteSequence(folder_id)

#### Edit

e.g. edit a folder

	benchlingapi.patchFolder(name=None, description=None, owner=None)

e.g. edit a sequence

	benchlingapi.patchsequence(name=None, bases=None, circular=None,
                      folder=None, description=None, color=None)

## BenchlingPortal

Not supported for non-aquarium users
