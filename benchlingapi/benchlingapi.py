import requests
import json
import os
from urllib2 import urlopen
from bs4 import BeautifulSoup
import re
import warnings

class BenchlingAPIException(Exception):
    """Generic Exception for BenchlingAPI"""

class BenchlingLoginError(Exception):
    '''Errors for incorrect login credentials'''

class AquariumLoginError(Exception):
    '''Errors for incorrect Aquarium login credentials'''

def verbose(func):
    '''
    Prints the response of a function
    :param func:
    :return:
    '''
    def wrapper(*params):
        result = func(*params)
        print result
        return result
    return wrapper

class RequestDecorator(object):
    def __init__(self, status_code):
        self.code = status_code

    def __call__(self, f):
        def wrapped_f(*args):
            args = list(args)
            args[1] = os.path.join(args[0].home, args[1])
            r = f(*args)
            if not r.status_code == self.code:
                    http_codes = {
                         200: "OK - Request was successful",
                         201: "CREATED - Resource was created",
                         400: "BAD REQUEST",
                         401: "UNAUTHORIZED",
                         403: "FORBIDDEN",
                         404: "NOT FOUND",
                         500: "INTERNAL SERVER ERROR"}
                    raise BenchlingAPIException("HTTP Response Failed {} {}".format(
                            r.status_code, http_codes[r.status_code]))
            return json.loads(r.text)
        return wrapped_f

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

    @RequestDecorator(201)
    def _post(self, what, data):
        return requests.post(what, json=data, auth=self.auth)

    @RequestDecorator(201)
    def _patch(self, what, data):
        return requests.patch(what, json=data, auth=self.auth)

    @RequestDecorator(200)
    def _get(self, what):
        return requests.get(what, auth=self.auth)

    @RequestDecorator(200)
    def _delete(self, what):
        return requests.delete(what, auth=self.auth)



    def delete_folder(self, id):
        self._delete('folders/{}'.format(id))

    def delete_sequence(self, id):
        self._delete('sequences/{}'.format(id))

    def patch_folder(self, name=None, description=None, owner=None):
        payload = {
            'name': name,
            'description': description,
            'owner': owner
        }
        self._clean_dictionary(payload)
        self._patch('folders/{}'.format(id))

    def patch_sequence(self, name=None, bases=None, circular=None,
                       folder=None, description=None, color=None):
        payload = {
            'name': name,
            'description': description,
            'bases': bases,
            'circular': circular,
            'folder': folder,
             'color': color
            }
        self._clean_dictionary(payload)
        self._patch('sequences/{}'.format(id))

    def create_folder(self, name, description=None, owner=None):
        payload = {
            'name': name,
            'description': description,
            'owner': owner
        }
        self._clean_dictionary(payload)
        self._post('folders/', payload)

    def create_sequence(self, name, bases, circular, folder, description=None, annotations=None):
        payload = {
            'name': name,
            'description': description,
            'bases': bases,
            'circular': circular,
            'folder': folder,
            'annotations': annotations
        }
        self._clean_dictionary(payload)
        self._post('sequences/', payload)

    def get_folder(self, id):
        return self._get('folders/{}'.format(id))

    def get_sequence(self, id):
        return self._get('sequences/{}'.format(id))

    def _clean_dictionary(self, dic):
        keys = dic.keys()
        for key in keys:
            if dic[key] is None:
                dic.pop(key)
        return dic



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
        return self.find_sequence(name, query='name')

    def _find(self, what, dic, value, query='name'):
        item_id = -1
        if query == 'id':
            item_id = value
        elif query == 'name':
            name = value
            items = dic[name]
            if len(items) == 0:
                raise BenchlingAPIException("No items found with {} {}".format(query, value))
            elif len(items) > 1:
                warnings.warn("More {} items found with {} {}".format(len(items), query, value))
                print items
            item = items[0]
            item_id = item['id']
        else:
            raise BenchlingAPIException("Query {} not understood. Could not find item.".format(query))
        return self._get(os.path.join(what, item_id))

    def find_sequence(self, value, query='name'):
        self._find('sequences', self.seq_dict, value, query=query)

    def find_folder(self, value, query='name'):
        self._find('folders', self.seq_dict, value, query=query)

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
