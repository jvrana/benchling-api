import coral as cor
import re
from aquariumapi import AquariumAPI
from aquariumapi import models
import subprocess
from .benchlingapi import BenchlingAPI, BenchlingAPIException, AquariumLoginError, BenchlingLoginError
import requests

class BenchlingPortal(BenchlingAPI):

    def __init__(self, bench_api_key, aq_url, aq_user, aq_api_key, home='https://api.benchling.com/v1/'):
        BenchlingAPI.__init__(self, bench_api_key, home=home)
        try:
            self.AqAPI = AquariumAPI(
                aq_url,
                aq_user,
                aq_api_key)
        except requests.ConnectionError as e:
            raise AquariumLoginError('Aquarium Login Credentials Incorrect. {} {}'.format(aq_user, aq_api_key))
        except TypeError as e:
            raise AquariumLoginError('Aquarium url likely incorrect. {}'.format(aq_url))

    def convertToCoral(self, benchling_seq):
        bs = benchling_seq
        c = cor.DNA(
        bs['bases'],
        bottom=None,
        topology = 'circular' if bs['circular'] else 'linear',
        stranded = 'ds',
        name=bs['name'])
        for a in bs['annotations']:
            if a['type'] == '':
                a['type'] = 'misc_feature'
            f = cor.Feature(
                a['name'].encode('utf-8').strip(),
                a['start'],
                a['end'],
                a['type'].encode('utf-8').strip(),
                strand = 0 if a['strand'] == 1 else 1,
                qualifiers = {
                    'label': a['name'],
                    'ApEinfo_fwdcolor': [a['color']],
                    'ApEinfo_revcolor': [a['color']]}
                    )
            f.color = a['color']
            c.features.append(f)
        return c

    def convertCoralToBenchling(self, coral_dna):
        d = coral_dna
        s = {}
        s['bases'] = str(d)
        s['circular'] = True if d['topology'] == 'circular' else False
        s['name'] = d['name']
        s['folder'] = 'lib_qCSi9wd8'

    def getShareLink(self, value, query='id'):
        ''' Collects share_link from Aquarium sample

        :param value: value to search aquarium
        :type value: str or int
        :param query: query identifier for searching aquarium
        :type query: str
        :returns: sequence url link
        :rtype: str

        '''
        results = self.AqAPI.find('sample', {query: value})
        if len(results['rows']) == 0:
            raise BenchlingAPIException('Could not find sample with query {} and value {}'.format(query, value))
        sample = results['rows'][0]
        share_link = ''
        try:
            share_link = sample['fields']['Sequence']
        except KeyError as e:
            sample_type = self.AqAPI.find('sample_type', {'id': sample['sample_type_id']})['rows'][0]
            print sample_type
            if sample_type['name'] not in ['Plasmid', 'Fragment']:
                raise BenchlingAPIException('Could not find Sequence in aquarium sample {}. \
                Sample is of sample type {} not a Fragment or Plasmid. \
                Error Message: {}'.format(sample_type['name'], sample['id'], e))
        return share_link

    def getSequenceFromAquarium(self, value, query='id'):
        ''' Collects sequence from Aquarium sample

        :param value: value to search aquarium
        :type value: str or int
        :param query: query identifier for searching aquarium
        :type query: str
        :returns: coral DNA sequence
        :rtype: Coral.DNA

        '''
        share_link = self.getShareLink(value, query=query)
        if share_link == '':
            message = "No share link found for plasmid {}: {}".format(query, value)
            raise BenchlingAPIException(message)
        elif not self._verifyShareLink(share_link):
            message = "Share link incorrectly formatted. Expected format {}. Found {}".format('https://benchling.com/s/\w+/edit', share_link)
            raise BenchlingAPIException(message)
        print share_link
        benchlingsequence = self.getSequenceFromShareLink(share_link)
        return self.convertToCoral(benchlingsequence)

    def _verifyShareLink(self, share_link):
        f = 'https://benchling.com/s/(\w+)/edit'
        result = re.match(f, share_link)
        return result != None

    def getPrimerSequenceFromAquarium(self, value, query):
        pass

    def makeCoralDNA(self, sequence):
        pass
