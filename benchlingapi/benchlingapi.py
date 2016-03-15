import requests
import json
import os
from urllib2 import urlopen
from bs4 import BeautifulSoup
import re

class BenchlingAPIException(Exception):
    """Generic Exception for BenchlingAPI"""

class BenchlingLoginError(Exception):
    '''Errors for incorrect login credentials'''

class AquariumLoginError(Exception):
    '''Errors for incorrect Aquarium login credentials'''

# Benchling API Info: https://api.benchling.com/docs/#sequence-sequence-collections-post
class BenchlingAPI(object):
    ''' Connector to BenchlingAPI '''

    def __init__(self, api_key, home='https://api.benchling.com/v1/'):
        '''
        :param key: Benchling API key.
        :type key: str
        :param home: Benchling API url
        :type login:

        '''
        self.home = 'https://api.benchling.com/v1/'
        self.auth = (api_key, '')
        self.seq_dict = {} #seq_name: seq_information
        self.folder_dict = {} #folder_name: folder_information
        try:
            self._createDictionaries()
        except requests.ConnectionError:
            raise BenchlingLoginError('Benchling login credentials incorrect. Check \
                BenchlinAPIKey: {}'.format(api_key))

    def _post(self, what, payload):
        '''Not yet implemented.'''

        raise NotImplementedError('Benchling does not yet support POST requests.')
        f = os.path.join(self.home, what)
        r = requests.get(f, data=payload, auth=self.auth)

    def _get(self, what, verbose=False):
        ''' Get request from Benchling

        :param what: request to get. Will be appended to self.home
        :type what: str
        :param verbose: whether to print response
        :type verbose: boolean
        :returns: json response
        :rtype: str

        '''
        if verbose:
            print "\tCall:", what
        r = requests.get(os.path.join(self.home, what), auth=self.auth)
        d = json.loads(r.text)
        if verbose:
            print "\tResponse:", r
        return d

    def _verifyShareLink(self, share_link):
        f = 'https://benchling.com/s/(\w+)'
        result = re.search(f, share_link)
        return result != None

    def _getSequenceNameFromShareLink(self, share_link):
        ''' A really hacky way to get a sequence
        name from a Benchling share link

        :param share_link: A benchling share link
        :type share_link: str
        :returns: Name of Benchling Sequence
        :rtype: str
        '''
        # try:
        #     print share_link
        #     gp = re.search('/seq-\w+-([-_\w]+)/edit', share_link)
        #     return gp.group(1)
        # except Exception as e:
        #     print e
        if not self._verifyShareLink(share_link):
            message = "Share link incorrectly formatted. Expected format {}. Found {}".format('https://benchling.com/s/\w+/edit', share_link)
            raise BenchlingAPIException(message)
        f = urlopen(share_link)
        soup = BeautifulSoup(f.read())
        title = soup.title.text
        gp = re.search("(.+)\s.\sBenchling", title)

        return gp.group(1)

    def getSequenceFromShareLink(self, share_link):
        ''' A really hacky way to get a sequence
        from a Benchling share link

        :param share_link: A benchling share link
        :type share_link: str
        :returns: Benchling API sequence information
        :rtype: dict
        '''
        name = self._getSequenceNameFromShareLink(share_link)
        return self.getSequence(name, query='name')

    def getSequence(self, value, query='name'):
        ''' Collects a sequence from Benchling according
        to some query

        :param value: query value
        :type value: str
        :param query: query type (i.e. 'name', 'id', etc.)
        :type query: str
        :returns: Benchling API sequence information
        :rtype: dict
        :raises Exception if query not valid
        '''
        if query == 'id':
            return self._get('sequences/{}'.format(value))
        elif query == 'name':
            name = value
            seqs = self.seq_dict[name]
            if len(seqs) == 0:
                raise Exception("No sequences found with {} {}".format(query, value))
            elif len(seqs) > 1:
                print "Warning: More than one sequence found with with {} {}. {} found.".format(query, value, len(seqs))
                print seqs
            seq = seqs[0]
            seq_id = seq['id']
            return self._get('sequences/{}'.format(seq_id))
        else:
            raise Exception("Query identifier not found")

    def getAllSequences(self):
        return self.seq_dict

    def getAllFolders(self):
        return self.folder_dict

    def _createDictionaries(self):
        r = self._get('folders')
        if 'error' in r:
            raise requests.ConnectionError('Benchling Authentication Required. Check your Benchling API key.')
        self.folders = r['folders']
        #global folders
        #self.folders = folders
        fd = self.folder_dict
        sd = self.seq_dict
        for f in self.folders:
            seqs = f['sequences']
            if f['name'] not in fd:
                fd[f['name']] = []
            fd[f['name']].append(f)
            for s in seqs:
                if s['name'] not in sd:
                    sd[s['name']] = []
                sd[s['name']].append(s)
