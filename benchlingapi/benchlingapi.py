import requests
import json
import os
from urllib2 import urlopen
from bs4 import BeautifulSoup
import re
import warnings
#TODO: Refactor code

class BenchlingAPIException(Exception):
    """Generic Exception for BenchlingAPI"""


class BenchlingLoginError(Exception):
    """Errors for incorrect login credentials"""


class AquariumLoginError(Exception):
    """Errors for incorrect Aquarium login credentials"""


class RequestDecorator(object):
    def __init__(self, status_codes):
        if not isinstance(status_codes, list):
            status_codes = [status_codes]
        self.code = status_codes

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            args = list(args)
            args[1] = os.path.join(args[0].home, args[1])
            r = f(*args)
            if r.status_code not in self.code:
                http_codes = {
                    200: "OK - Request was successful",
                    201: "CREATED - Resource was created",
                    400: "BAD REQUEST",
                    401: "UNAUTHORIZED",
                    403: "FORBIDDEN",
                    404: "NOT FOUND",
                    500: "INTERNAL SERVER ERROR",
                    504: "SERVER TIMEOUT"}
                raise BenchlingAPIException("HTTP Response Failed {} {}".format(
                    r.status_code, http_codes[r.status_code]))
            return json.loads(r.text)

        return wrapped_f


class UpdateDecorator(object):
    def __init__(self):
        pass

    def __call__(self, f):
        def wrapped_f(obj, *args, **kwargs):
            r = f(obj, *args, **kwargs)
            obj._update_dictionaries()
            return r

        return wrapped_f


class Verbose(object):
    def __init__(self):
        pass

    def __call__(self, f):
        def wrapped_f(obj, *args, **kwargs):
            print f.__name__, 'started'
            r = f(obj, *args, **kwargs)
            print f.__name__, 'ended'
            return r

        return wrapped_f


# Benchling API Info: https://api.benchling.com/docs/#sequence-sequence-collections-post
class BenchlingAPI(object):
    ''' Connector to BenchlingAPI '''

    # TODO: Create SQLite Database for sequences
    def __init__(self, api_key, home='https://api.benchling.com/v1/'):
        '''
        :param api_key: Benchling API key.
        :type api_key: str
        :param home: Benchling API url
        :type home: str

        '''
        self.home = home
        self.auth = (api_key, '')
        self.seq_dict = {}  # seq_name: seq_information
        self.folder_dict = {}  # folder_name: folder_information
        self.folders = []
        self.sequences = []
        self.proteins = []
        try:
            self._update_dictionaries()
        except requests.ConnectionError:
            raise BenchlingLoginError('Benchling login credentials incorrect. Check \
                BenchlinAPIKey: {}'.format(api_key))

    @RequestDecorator([200, 201])
    def _post(self, what, data):
        return requests.post(what, json=data, auth=self.auth)

    @RequestDecorator([200, 201])
    def _patch(self, what, data):
        return requests.patch(what, json=data, auth=self.auth)

    @RequestDecorator(200)
    def _get(self, what, data=None):
        if data is None:
            data = {}
        return requests.get(what, json=data, auth=self.auth)

    @RequestDecorator(200)
    def _delete(self, what):
        return requests.delete(what, auth=self.auth)

    #TODO add request decorator
    @RequestDecorator(200)
    def delete_folder(self, id):
        #raise BenchlingAPIException("Benchling does not yet support deleting folders through the API")
        return self._delete('folders/{}'.format(id))

    @Verbose()
    def delete_sequence(self, id):
        d = self._delete('sequences/{}'.format(id))
        # TODO: Update dictionaries and lists after delete
        return d

    @Verbose()
    def patch_folder(self, name=None, description=None, owner=None, type=type):
        payload = {
            'name': name,
            'description': description,
            'owner': owner,
            'type': type
        }
        self._clean_dictionary(payload)
        return self._patch('folders/{}'.format(id))

    @Verbose()
    def patch_sequence(self, name=None, bases=None, circular=None,
                       folder=None, description=None, color=None, aliases=None):
        payload = {
            'name': name,
            'aliases': aliases,
            'description': description,
            'bases': bases,
            'circular': circular,
            'folder': folder,
            'color': color
        }
        self._clean_dictionary(payload)
        return self._patch('sequences/{}'.format(id))

    @Verbose()
    def create_folder(self, name, description=None, folder_type='INVENTORY'):
        payload = dict(name=name, description=description, owner=self.getme()['id'], type=folder_type)
        self._clean_dictionary(payload)
        return self._post('folders/', payload)

    @Verbose()
    def create_sequence(self, name, bases, circular, folder, description=None, annotations=None, aliases=None):
        """
        :param name: Name of the sequence as a Str
        :param bases: Basepairs as a Str
        :param circular: True or False
        :param folder: folder_id as a Str
        :param description: description of the sequence
        :param annotations:
        :param aliases:
        :return:
        """
        payload = {
            'name': name,
            'description': description,
            'bases': bases,
            'circular': circular,
            'folder': folder,
            'annotations': annotations,
            'aliases': aliases
        }
        self._clean_dictionary(payload)
        return self._post('sequences/', payload)

    def folder_exists(self, value, query='name', regex=False):
        folders = self.filter_folders({query: value}, regex=regex)
        if len(folders) > 0:
            return True
        else:
            return False

    def sequence_exists(self, value, query='name', regex=False):
        sequences = self.filter_sequences({query: value}, regex=regex)
        if len(sequences) > 0:
            return True
        else:
            return False

    @staticmethod
    def _filter(item_list, fields, regex=False):
        '''
        Filters a list of dictionaries based on a set
        of fields. Can search using regular expressions
        if requested.
        :param item_list:
        :param fields:
        :param regex:
        :return:
        '''
        filtered_list = []
        for item in item_list:
            a = True
            for key in fields:
                if regex:
                    g = re.search(fields[key], item[key])
                    if g is None:
                        a = False
                        break
                else:
                    if not item[key] == fields[key]:
                        a = False
                        break
            if a == True:
                filtered_list.append(item)
        return filtered_list

    def filter_sequences(self, fields, regex=False):
        '''
        Filters sequences based on a set of fields. Can search for
        regular expressions if requested.
        :param fields:
        :param regex:
        :return:
        '''
        return self._filter(self.sequences, fields, regex=regex)

    def filter_folders(self, fields, regex=False):
        '''
        Filters folders based on a set of fields. Can search for
        regular expressions if requested.
        :param fields:
        :param regex:
        :return:
        '''
        return self._filter(self.folders, fields, regex=regex)

    def _find(self, what, dict, value, query='name', regex=False):
        items = []
        try:
            items = self._filter(dict, {query: value}, regex=regex)
        except KeyError:
            raise BenchlingAPIException("Query {} not understood. Could not find item.".format(query))
        if len(items) == 0:
            raise BenchlingAPIException("No items found with {} \'{}\'.".format(query, value))
        elif len(items) > 1:
            warnings.warn("More {} items found with {} \'{}\'. Returning first item.".format(len(items), query, value))
        item = items[0]
        return self._get(os.path.join(what, item['id']))

    def find_sequence(self, value, query='name', regex=False):
        return self._find('sequences', self.sequences, value, query=query, regex=regex)

    def find_folder(self, value, query='name', regex=False):
        return self._find('folders', self.folders, value, query=query, regex=regex)

    def get_folder(self, id):
        return self._get('folders/{}'.format(id))

    @staticmethod
    def _clean_annotations(sequence):
        '''
        Cleans up the sequence start and end points in the unusual case
        where end == 0
        :param sequence:
        :return:
        '''
        annotations = sequence['annotations']
        for a in annotations:
            if a['end'] == 0:
                a['end'] = len(sequence['bases'])

    def get_sequence(self, seq_id, data=None):
        if data is None:
            data = {}
        sequence = self._get('sequences/{}'.format(seq_id), data=data)
        self._clean_annotations(sequence)
        return sequence

    @staticmethod
    def _clean_dictionary(dic):
        keys = dic.keys()
        for key in keys:
            if dic[key] is None:
                dic.pop(key)
        return dic

    def _verifysharelink(self, share_link):
        f = 'https://benchling.com/s/(\w+)'
        result = re.search(f, share_link)
        verified = result is not None
        if not verified:
            message = "Share link incorrectly formatted. Expected format {}. Found {}".format(
                'https://benchling.com/s/\w+/edit', share_link)
            raise BenchlingAPIException(message)

    def _opensharelink(self, share_link):
        self._verifysharelink(share_link)
        f = urlopen(share_link)
        soup = BeautifulSoup(f.read())
        return soup

    def _getsequenceidfromsharelink(self, share_link):
        seq = None
        try:
            soup = self._opensharelink(share_link)
            for s in soup.findAll():
                g = re.search('\"folder_item_ids\": \[\"seq_(\w+)\"\]', s.text)
                if not g == None:
                    seq = "seq_{}".format(g.group(1))
                    break
        except:
            d = self._parseURL(share_link)
            seq = d['seq_id']
        return seq

    @staticmethod
    def _parseURL(url):
        g = re.search('benchling.com/(?P<user>\w+)/f/(?P<folderid>\w+)' + \
                      '-(?P<foldername>\w+)/seq-(?P<seqid>\w+)-(?P<seqname>' + \
                      '[a-zA-Z0-9_-]+)', url)
        labels = ['user', 'folder_id', 'folder_name', 'seq_id', 'seq_name']
        d = dict(zip(labels, g.groups()))
        d['seq_id'] = 'seq_{}'.format(d['seq_id'])
        return d

    def getsequencefromsharelink(self, share_link):
        ''' A really hacky way to get a sequence
        from a Benchling share link

        :param share_link: A benchling share link
        :type share_link: str
        :returns: Benchling API sequence information
        :rtype: dict
        '''
        id = self._getsequenceidfromsharelink(share_link)
        return self.get_sequence(id)

    def getseqlist(self):
        return self.sequences

    def getfolderlist(self):
        return self.folders

    def getme(self):
        return self._get('entities/me')

    def _clear(self):
        self.folders = []
        self.sequences = []
        self.seq_dict = {}
        self.folder_dict = {}

    def _updatelistsfromdictionaries(self):
        for f in self.folders:
            seqs = f['sequences']
            if f['name'] not in self.folder_dict:
                self.folder_dict[f['name']] = []
            self.folder_dict[f['name']].append(f)
            for s in seqs:
                s['folder'] = f['id']
                if s not in self.sequences:
                    self.sequences.append(s)
                if s['name'] not in self.seq_dict:
                    self.seq_dict[s['name']] = []
                self.seq_dict[s['name']].append(s)

    def _update_dictionaries(self):
        self._clear()
        r = self._get('folders')
        if 'error' in r:
            raise requests.ConnectionError('Benchling Authentication Required. Check your Benchling API key.')
        self.folders = r['folders']
        self._updatelistsfromdictionaries()

    def search(self, query, querytype='text', limit=10, offset=0):
        return self._post('search', {'query': query, 'queryType': querytype, 'limit': limit, 'offset': offset})


        # TODO Add protein functions
        # TODO add alignment functions?
        # TODO add task functions
