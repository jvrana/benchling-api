[![travis build](https://img.shields.io/travis/klavinslab/benchling-api.svg)](https://travis-ci.org/klavinslab/benchling-api)


Branch | Coverage
:---: | :---:
**master** | [![Coverage Status](https://coveralls.io/repos/github/klavinslab/benchling-api/badge.svg?branch=master)](https://coveralls.io/github/klavinslab/benchling-api?branch=master)
**development** | [![Coverage Status](https://coveralls.io/repos/github/klavinslab/benchling-api/badge.svg?branch=development)](https://coveralls.io/github/klavinslab/benchling-api?branch=development)

# Description
Benchling provides a convenient way to store DNA sequences (plasmids, primers, pcr
fragments, etc.) for an entire lab. This repo provides a convinient wrapper for
making Benchling API requests.

<b>Features:</b>
<ul>
<li>Accessing Benchling sequences and folders</li>
<li>Creating new sequences and folders</li>
<li>Searching through sequences and folders using regular expressions</li>
<li>Converting Benchling sequence JSON to genbank or FASTA files</li>
<li>Opening and accessing sequences in a Benchling Share links</li>
</ul>

# Installation
	cd directory/that/contains/benchling-api
	pip install .

# Usage

## Initializing the API object

The BenchlingAPI object provides an interface for accessing Benchling sequences. 
It requires a benchling API-key, which can be requested from Benchling. More information
on the Benchling API can be accessed here: https://api.benchling.com/docs/.

	from benchlingapi import BenchlingAPI
	
	bench_api_key = 'sk_g7fo2vxskNUYffNPkShOFIsOmtY9ejIXX'
	benchlingapi = BenchlingAPI(bench_api_key)

The first argument is the Benchling API key, which can be requested through benchling and accessed by scrolling to the bottom of you account information on Benchling.

#### Find

getting folders
```json
{'count': 59, 'created_at': '2013-10-01T20:07:18+00:00', 'description': '', 'id': 'lib_pP6d50rJn1', 'modified_at': '2017-01-20T21:57:55.991758+00:00', 'name': 'Plasmids', 'owner': 'ent_A7BlnCcJTU', 'permissions': {'admin': True, 'appendable': True, 'owner': False, 'readable': True, 'writable': True}, 'sequences': [{'id': 'seq_wHiaXdFM', 'name': 'pGPT4-pGAL1-G(m)AVNY', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_WQ0wqb9f', 'name': 'pMODU6-pGALZ4-iaaH', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_okitCPyx', 'name': 'pGPT4-pGAL1-GAVNY(VP64)', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_bw3XWuZU', 'name': 'pMODT4-pGALZ4-AVNY', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_K5hwGNwg', 'name': 'pMODU6-pGAL1-BleoMX', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_AyQ7ToIn', 'name': 'pBR322 (Sample Sequence)', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_t77GYXRB', 'name': 'pGPT4-pGAL1-EGFP', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_5bmPzcKN', 'name': 'pMODU6-pGALZ4-NatMX', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_Na2oNxzs', 'name': 'pMODU6-pGALZ4-FAR1-mut-87aa', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_0FmHFzJe', 'name': 'pMODT4-pGAL1-attB1-GAVNY', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_m42PVReQ', 'name': 'pMODT4-pGALZ4-Z4AVNY', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_mfMW58Dd', 'name': 'pGPL5G-pGALZ4-URA3', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_QteKmJdS', 'name': 'pGPT4-pGAL1-GAVNY_mutated_library', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_usn0K27s', 'name': 'pMODU6-pGALZ4-BleoMX', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_i0Yl6uzk', 'name': 'pMODH8-pGPD-TIR1_DM', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_TWAJLtvz', 'name': 'pMODU6-pGAL1-P1G1-HygMX', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_2rKmILGU', 'name': 'pMODU6-pGAL1-NatMX', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_5AXMlSvB', 'name': 'pYMOD2Kmx_pGAL1-HYG_pGAL1-iaah', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_qihkmlW4', 'name': 'pMODU6-pGAL1-AlphaFactor', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_k0MuYdIM', 'name': 'pMODU6-pGAL1-IAA17T2-FAR1', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_7yXay7Ep', 'name': 'pGP8G-TIR1-Y', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_GuqSGBXY', 'name': 'pGPT4-pGAL1-GAVNY(VP64) new design', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_fkFjzKkb', 'name': 'v63_pGP8zGAL-STE5(-)RING-SNC2 C-term', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_PKJNfuZA', 'name': 'pGPH8-pGAL1-GAVNY_v2', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_f4GgnFdY', 'name': 'pGPT4-pGAL1-GAVNY_seq_verified', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_SGfG2YeB', 'name': 'pMODU6-pGALZ4-HygMX', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_vA5dxrqd', 'name': 'pMODU6-pGALZ4-AlphaFactor', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_tMz0Xv3g', 'name': 'pMODU6-pGAL1-FAR1-L1-IAA17T2', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_2xGw2yCj', 'name': 'pGPH8-pGAL1-GAVNY', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_rwDoRd9Q', 'name': 'pMODU6-pGALZ4-FAR1', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_ri07UntS', 'name': 'pMODU6-pGPD-EYFP', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_TsTM0B8q', 'name': 'pMOD4-pGAL1Z3(P3)-MF(AL', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_QGfqobtP', 'name': 'pGPT4-pGAL1-AVNY', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_9ph0SnJV', 'name': 'AmpR-T4-pGAL1-GAL4DBD-L1', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_F4tEc0XU', 'name': 'pMODU6-pGALZ4-STE5(-)RING', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_iGdjEEx4', 'name': 'pGPT4-pGAL1-P1G1-GEV', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_hhI5TTbO', 'name': 'pMODU6-pGAL1-FAR1-IAA17T2', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_AgQ1w9ak', 'name': 'pLAB2', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_y9xdtVx7', 'name': 'pMODKan-HO-pACT1GEV', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_D1iAdKMz', 'name': 'pGPL5G-pGAL1-URA3', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_etTsAfD4', 'name': 'pGPU6-pGALZ4-eYFP', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_5HcRWKi8', 'name': 'pMODU6-pGALZ4-P1G1-HygMX', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_Qc6f2Kii', 'name': 'pMOD4G-NLS_dCas9_VP64', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_VazadBJw', 'name': 'pGPT4-pGAL1-GAVNY', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_ztl4dnOW', 'name': 'pLAB1', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_kKtPZ1Rs', 'name': 'pMODT4-pGAL1-P1G1-GAVNY', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_4ccBmI1j', 'name': 'pGPU6-pGAL1-AFB2', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_tFGIIL0C', 'name': 'pMODU6-pGAL1-FAR1', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_7O7ThYSI', 'name': 'pMODU6-pGALZ4-Z4AVNY', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_w2IZPFzd', 'name': 'pMODOK-pACT1-GAVNY', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_UbsucV1t', 'name': 'pMODU6-pGAL1-HygMX', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_Nv6wYspV', 'name': 'FAR1-mut-87aa-TP', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_rzQGBzv2', 'name': 'pGP5G-ccdB', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_QuWMpfRK', 'name': 'pMODT4-pGAL1-attB1-GVNY', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_l5VHTc8Z', 'name': 'pGPU6-pGAL1-TIR1_DM', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_6VN5FDpP', 'name': 'pMODOK-pACT1-GAVN', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_2MFFshfl', 'name': 'pYMOD2Kmx_pGAL1-HYG_ZEV4-cassette', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_IyZI9bEh', 'name': 'pMODU6-pGAL1-FAR1-L1-IAA17T1_opt', 'folder': 'lib_pP6d50rJn1'}, {'id': 'seq_beOWphBv', 'name': 'pMODKan-HO-pACT1-ZEV4', 'folder': 'lib_pP6d50rJn1'}], 'type': 'ALL'}
```

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
