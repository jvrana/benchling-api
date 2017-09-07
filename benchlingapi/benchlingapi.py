import requests
import json
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import warnings
import base64

class BenchlingAPIException(Exception):
    """Generic Exception for BenchlingAPI"""


class BenchlingLoginError(Exception):
    """Errors for incorrect login credentials"""


class AquariumLoginError(Exception):
    """Errors for incorrect Aquarium login credentials"""


class RequestDecorator(object):
    """
    Wraps a function to raise error with unexpected request status codes
    """
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
                    403: "FORBIDDEN",
                    404: "NOT FOUND",
                    500: "INTERNAL SERVER ERROR",
                    503: "SERVICE UNAVAILABLE",
                    504: "SERVER TIMEOUT"}
                msg = ""
                if r.status_code in http_codes:
                    msg = http_codes[r.status_code]
                raise BenchlingAPIException("HTTP Response Failed {} {}".format(
                    r.status_code, msg))
            return json.loads(r.text)

        return wrapped_f


class UpdateDecorator(object):
    """
    Wraps a function to update the benchlingapi dictionary
    """
    def __init__(self):
        pass

    def __call__(self, f):
        def wrapped_f(obj, *args, **kwargs):
            r = f(obj, *args, **kwargs)
            obj._update_dictionaries()
            return r

        return wrapped_f


class Verbose(object):
    """
    Wraps a function to provide verbose mode for debugging requests
    """
    def __init__(self):
        pass

    def __call__(self, f):
        def wrapped_f(obj, *args, **kwargs):
            print(f.__name__, 'started')
            r = f(obj, *args, **kwargs)
            print(f.__name__, 'ended')
            return r

        return wrapped_f


# Benchling API Info: https://api.benchling.com/docs/#sequence-sequence-collections-post
class BenchlingAPI(object):
    """
    Connects to BenchlingAPI
    """

    # TODO: Create SQLite Database for sequences
    def __init__(self, api_key, home='https://api.benchling.com/v1/'):
        """
        BenchlingAPI connector
        :param api_key:
        :param home:
        """
        self.home = home
        self.auth = (api_key, '')
        self.seq_dict = {}  # seq_name: seq_information
        self.folder_dict = {}  # folder_name: folder_information
        self.folders = []
        self.sequences = []
        self.proteins = []
        try:
            self.update()
        except requests.ConnectionError:
            raise BenchlingLoginError('Benchling login credentials incorrect. Check \
                BenchlinAPIKey: {}'.format(api_key))

    def update(self):
        """
        Updates the api dictionaries
        :return:
        """
        self._update_dictionaries()

    @RequestDecorator([200, 201, 202])
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

    # TODO add request decorator
    @RequestDecorator(200)
    def delete_folder(self, id):
        """
        Deletes a Benchling folder by id
        :param id:
        :return:
        """
        # raise BenchlingAPIException("Benchling does not yet support deleting folders through the API")
        return self._delete('folders/{}'.format(id))

    @Verbose()
    def delete_sequence(self, id):
        """
        Deletes a Benchling sequence by id
        :param id:
        :return:
        """
        d = self._delete('sequences/{}'.format(id))
        # TODO: Update dictionaries and lists after delete
        return d

    @Verbose()
    def patch_folder(self, id, name=None, description=None, owner=None, type=type):
        """
        Updates a folder with id
        :param name:
        :param description:
        :param owner:
        :param type:
        :return:
        """
        payload = {
            'name': name,
            'description': description,
            'owner': owner,
            'type': type
        }
        self._clean_dictionary(payload)
        return self._patch('folders/{}'.format(id))

    @Verbose()
    def patch_sequence(self, id, name=None, bases=None, circular=None,
                       folder=None, description=None, color=None, aliases=None):
        """
        Updates a sequence
        :param name:
        :param bases:
        :param circular:
        :param folder:
        :param description:
        :param color:
        :param aliases:
        :return:
        """
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
        """
        Creates a new folder
        :param name:
        :param description:
        :param folder_type:
        :return:
        """
        payload = dict(name=name, description=description, owner=self.getme()['id'], type=folder_type)
        self._clean_dictionary(payload)
        return self._post('folders/', payload)

    # TODO: Add a replace option for creating a sequence with same name at the folder
    @Verbose()
    def create_sequence(self, name, bases, circular, folder,
                        description=None, annotations=None,
                        aliases=None, tags=None, overwrite=False):
        """
        Creates a new sequences
        :param name:
        :param bases:
        :param circular:
        :param folder:
        :param description:
        :param annotations:
        :param aliases:
        :param tags:
        :param overwrite:
        :return:
        """
        payload = {
            'name': name,
            'description': description,
            'bases': bases,
            'circular': circular,
            'folder': folder,
            'annotations': annotations,
            'aliases': aliases,
            'tags': tags
        }

        # Get list of previous sequences
        # Delete if overwrite
        prev_seq_ids = set()
        for seq in self.get_folder(folder)['sequences']:
            if overwrite and str(seq['name']) == str(name):
                print('Overwrite on: deleting seq {}'.format(seq['id']))
                self.delete_sequence(seq['id'])
                prev_seq_ids.add(seq['id'])

        # Post the sequence
        self._clean_dictionary(payload)
        self._post('sequences/', payload)

        # Find the newly created sequence
        for seq in self.get_folder(folder)['sequences']:
            if seq['name'] == name and seq['id'] not in prev_seq_ids:
                return self.get_sequence(seq['id'])

        # Else something wrong happened
        raise BenchlingAPIException("Unable to return newly created sequence. \
                Sequence may have been created nevertheless.")

    def folder_exists(self, value, query='name', regex=False):
        """
        Whether a Benchling folder already exists
        :param value:
        :param query:
        :param regex:
        :return:
        """
        folders = self.filter_folders({query: value}, regex=regex)
        if len(folders) > 0:
            return True
        else:
            return False

    def sequence_exists(self, value, query='name', regex=False):
        """
        Whether a Benchling sequence already exists
        :param value:
        :param query:
        :param regex:
        :return:
        """
        sequences = self.filter_sequences({query: value}, regex=regex)
        if len(sequences) > 0:
            return True
        else:
            return False

    @staticmethod
    def _filter(item_list, fields, regex=False):
        """
        Filters a list of dictionaries based on a set
        of fields. Can search using regular expressions
        if requested. Uses the cached data stored in the api object.
        :param item_list:
        :param fields:
        :param regex:
        :return:
        """
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
        """
        Filters sequences based on a set of fields. Can search for
        regular expressions if requested. Uses the cached data stored in the api object.
        :param fields:
        :param regex:
        :return:
        """
        return self._filter(self.sequences, fields, regex=regex)

    def filter_folders(self, fields, regex=False):
        """
        Filters folders based on a set of fields. Can search for
        regular expressions if requested. Uses the cached data stored in the api object.
        :param fields:
        :param regex:
        :return:
        """
        return self._filter(self.folders, fields, regex=regex)

    def _find(self, what, dict, value, query='name', regex=False):
        """
        Uses the cached data stored in the api object to find the item
        :param what:
        :param dict:
        :param value:
        :param query:
        :param regex:
        :return:
        """
        item = self._find_cached_items(dict, query, regex, value)[0]
        return self._get(os.path.join(what, item['id']))

    def _find_cached_items(self, dict, query, regex, value):
        """
        Uses the cached data stored in teh api object to find items
        :param dict:
        :param query:
        :param regex:
        :param value:
        :return:
        """
        items = []
        try:
            items = self._filter(dict, {query: value}, regex=regex)
        except KeyError:
            raise BenchlingAPIException("Query {} not understood. Could not find item.".format(query))
        if len(items) == 0:
            raise BenchlingAPIException("No items found with {} \'{}\'.".format(query, value))
        elif len(items) > 1:
            warnings.warn("More {} items found with {} \'{}\'. Returning first item.".format(len(items), query, value))
        return items

    def find_sequence(self, value, query='name', regex=False):
        """
        Finds a sequence based on a id, name, or regex+name query
        :param value:
        :param query:
        :param regex:
        :return:
        """
        return self._find('sequences', self.sequences, value, query=query, regex=regex)

    def find_folder(self, value, query='name', regex=False):
        """
        Finds a folder based on a id, name, or regex+name query
        :param value:
        :param query:
        :param regex:
        :return:
        """
        return self._find('folders', self.folders, value, query=query, regex=regex)

    def get_folder(self, id):
        return self._get('folders/{}'.format(id))


    def submit_mafft_alignment(self, seq_id, queries,
                               adjust_direction="no",
                               max_iterations=0,
                               retree=2,
                               gap_open_penalty=1.53,
                               gap_extension_penalty=0):

        mafft_options = dict(
            adjust_direction=adjust_direction,
            max_iterations=max_iterations,
            retree=retree,
            gap_open_penalty=gap_open_penalty,
            gap_extension_penalty=gap_extension_penalty)
        return self.submit_alignment(seq_id, queries, 'mafft', mafft_options)

    def submit_clustalo(self, seq_id, queries,
            max_guidetree_iterations=10,
            max_hmm_iterations=25,
            mbed_guide_tree="yes",
            mbed_iteration="yes",
            num_combined_iterations=0):

        clustalo_options = dict(
            max_guidetree_iterations=max_guidetree_iterations,
            max_hmm_iterations=max_hmm_iterations,
            mbed_guide_tree=mbed_guide_tree,
            mbed_iteration=mbed_iteration,
            num_combined_iterations=num_combined_iterations,
        )

        return self.submit_alignment(seq_id, queries, 'clustalo', clustalo_options)


    def submit_alignment(self, seq_id, queries, algorithm, algorithm_options):
        files = [{'id': seq_id}]
        i = 0

        # if query is a tuple, then the data is already prepared
        # else if the query is a string it could be (1) a path to a fasta or ab1 file
        # (2) a benchling_sequence_id, or (3) encoded data with no name
        for q in queries:
            print(q)
            # if the query is a tuple
            if isinstance(q, tuple):
                files.append(dict(
                    name=q[0],
                    data=q[1]
                ))
            # if the query is a string
            elif isinstance(q, str):
                # if the query is a Benchling sequence_id
                if q.startswith('seq'):
                    files.append(dict(
                        id=q
                    ))
                # if the query is a file, encode the data
                elif os.path.exists(q):
                    data64=None
                    with open(q) as f:
                        data64 = base64.b64encode(f.read())
                    files.append(dict(
                        name=os.path.basename(q),
                        data=data64
                    ))
                # else, the data is already encoded and needs a name
                else:
                    files.append(dict(
                        name='untitled_{}'.format(i),
                        data=q
                    ))
                    i += 1

        data = {
            "algorithm": algorithm,
            "algorithmOptions": algorithm_options,
            "files": files
        }
        return self._post('alignments', data)

    # TODO: submit batched alignments that auto-updates once tasks are complete
    def submit_batched_alignment(self):
        pass

    def get_task(self, task_id):
        return self._get(os.path.join('tasks', task_id))

    def get_alignment(self, alignment_id):
        return self._get(os.path.join('alignments', alignment_id))

    @staticmethod
    def _clean_annotations(sequence):
        """
        Cleans up the sequence start and end points in the unusual case
        where end == 0
        :param sequence:
        :return:
        """
        annotations = sequence['annotations']
        for a in annotations:
            if a['end'] == 0:
                a['end'] = len(sequence['bases'])

    def get_sequence(self, seq_id, data=None):
        """
        Get a sequence from a sequence id
        :param seq_id:
        :param data:
        :return:
        """
        if data is None:
            data = {}
        sequence = self._get('sequences/{}'.format(seq_id), data=data)
        self._clean_annotations(sequence)
        return sequence

    @staticmethod
    def _clean_dictionary(dic):
        """
        Removes keys whose values are None
        :param dic:
        :return:
        """
        keys = list(dic.keys())
        for key in keys:
            if dic[key] is None:
                dic.pop(key)
        return dic

    def _verifysharelink(self, share_link):
        """
        Verifies a share_link is in the correct format
        :param share_link:
        :return:
        """
        f = 'https://benchling.com/s/(\w+)'
        result = re.search(f, share_link)
        verified = result is not None
        if not verified:
            message = "Share link incorrectly formatted. Expected format {}. Found {}".format(
                'https://benchling.com/s/\w+/edit', share_link)
            raise BenchlingAPIException(message)

    def _opensharelink(self, share_link):
        """
        Hacky way to read the contents of a Benchling share link
        :param share_link:
        :return:
        """
        self._verifysharelink(share_link)
        f = urlopen(share_link)
        soup = BeautifulSoup(f.read(), "lxml")
        return soup

    def _getsequenceidfromsharelink(self, share_link):
        seq = None
        try:
            soup = self._opensharelink(share_link)
            search_pattern = "seq_\w+"
            possible_ids = re.findall(search_pattern, soup.text)
            if len(possible_ids) == 0:
                raise BenchlingAPIException("No sequence ids found in sharelink html using search pattern {}".format(
                        search_pattern))
            uniq_ids = list(set(possible_ids))
            if len(uniq_ids) > 1:
                raise BenchlingAPIException("More than one possible sequence id found in sharelink html using search "
                                      "pattern {}".format(search_pattern))
            seq = uniq_ids[0]
        except BenchlingAPIException:
            d = self._parseURL(share_link)
            seq = d['seq_id']
        if seq is None:
            raise BenchlingAPIException("Could not find seqid in sharelink body or url.")
        return seq

    @staticmethod
    def _parseURL(url):
        """
        A really hacky way to parse the Benchling api. This may become unstable.
        :param url:
        :return:
        """
        g = re.search('benchling.com/(?P<user>\w+)/f/(?P<folderid>\w+)' + \
                      '-(?P<foldername>\w+)/seq-(?P<seqid>\w+)-(?P<seqname>' + \
                      '[a-zA-Z0-9_-]+)', url)
        labels = ['user', 'folder_id', 'folder_name', 'seq_id', 'seq_name']
        d = dict(list(zip(labels, g.groups())))
        d['seq_id'] = 'seq_{}'.format(d['seq_id'])
        return d

    def getsequencefromsharelink(self, share_link):
        """ A really hacky way to get a sequence
        from a Benchling share link

        :param share_link: A Benchling share link
        :type share_link: str
        :returns: Benchling API sequence information
        :rtype: dict
        """
        id = self._getsequenceidfromsharelink(share_link)
        return self.get_sequence(id)

    def getme(self):
        """
        Gets the user associated with this api
        :return:
        """
        return self._get('entities/me')

    def _clear(self):
        """
        Clears the api cache
        :return:
        """
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
        """
        Updates the dictionary cache for the api
        :return:
        """
        self._clear()
        r = self._get('folders')
        if 'error' in r:
            raise requests.ConnectionError('Benchling Authentication Required. Check your Benchling API key.')
        self.folders = r['folders']
        self._updatelistsfromdictionaries()

    def search(self, query, querytype='text', limit=10, offset=0):
        """
        Perform a Benchling search with text, bases, aminoAcids, or prosite
        :param query:
        :param querytype:
        :param limit:
        :param offset:
        :return:
        """
        return self._post('search', {'query': query, 'queryType': querytype, 'limit': limit, 'offset': offset})


        # TODO Add protein functions
        # TODO add alignment functions?
        # TODO add task functions
