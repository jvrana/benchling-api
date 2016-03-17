from nose.tools import assert_false, assert_true, assert_raises

class TestBenchlingAPI(object):

    def __init__(self):
        bench_api_key = 'sk_g7fo2vxkNUYNPkShOFIOmtY9ejIGE'
        aq_api_key = 'ZeMgEm1B9Hy7kt1KdUVFZlYV3bT7R7hSGE4YavrlVlc'
        aq_user = 'vrana'
        aq_url = 'http://54.68.9.194:81/api'
        import requests
        from benchlingapi import *
        credentials = [bench_api_key,
                               aq_url,
                               aq_user,
                               aq_api_key]
        self.portal = BenchlingPortal(*credentials)

    def test(self):
        print self.portal.seq_dict
        print self.portal.folder_dict
        print self.portal.getSequenceFromShareLink('https://benchling.com/s/SEt6YmhB/edit')

    def test_create_delete_sequence(self):
        # Find the test folder
        folder_name = 'apitestfolder'
        description = 'Folder created by nosetest'
        folder = self.portal.filterFolders({'name': folder_name})[0]
        folder2 = self.portal.findFolder(folder_name, query='name', regex=False)
        assert_true(folder == folder2)

        # Delete any previous sequences
        new_sequence_fields = {
            'name': 'NoseTestSequence',
            'circular': True,
            'folder': folder['id']
        }
        sequences = self.portal.filterSequences({'name': 'NoseTestSequence'}, regex=False)
        print sequences
        for s in sequences:
            self.portal.deleteSequence(s['id'])

        # Create new sequence and confirm created
        new_sequence = self.portal.createSequence("NoseTestSequence",
                                   "AGGTGTTGAGCAGA",
                                   True,
                                   folder['id'],
                                   description="Sequence created from the BenchlingAPI")
        print self.portal.filterSequences({'name': new_sequence['name']})
        print self.portal.getSequence(new_sequence['id'])['id']

        self.portal._updateDictionaries()
        # print new_sequence
        assert_true(self.portal.sequenceExists(new_sequence['name'], query='name'))
        assert_true(self.portal.sequenceExists(new_sequence['id'], query='id'))
        #
        # # Delete sequence and confirm deleted
        self.portal.deleteSequence(new_sequence['id'])
        print self.portal.filterSequences({'name': new_sequence['name']})
        self.portal._updateDictionaries()
        print self.portal.getSequence(new_sequence['id'])


t = TestBenchlingAPI()
t.test()
