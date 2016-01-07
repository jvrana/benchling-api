import coral as cor
import re
from aquariumapi import AquariumAPI
from aquariumapi import models
import subprocess
from .benchlingapi import BenchlingAPI, BenchlingAPIException, AquariumLoginError, BenchlingLoginError
import requests
import json

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

    # FIXME: Fix cases of start > stop and which stand
    def convertToCoral(self, benchling_seq):
        bs = benchling_seq
        c = cor.DNA(
        bs['bases'],
        bottom=None,
        topology = 'circular' if bs['circular'] else 'linear',
        stranded = 'ds',
        name=bs['name'])
        for a in bs['annotations']:
            name = a['name'].encode('utf-8').strip()
            start = a['start']
            stop = a['end']
            # if stop == 0:
            #     stop = len(c)
            # if start > stop:
            #     s = start
            #     start = stop
            #     stop = s
            strand = 0 if a['strand'] == 1 else 1
            qualifiers = {
                        'label': name,
                        'ApEinfo_fwdcolor': [a['color']],
                        'ApEinfo_revcolor': [a['color']]}
            type = a['type'].encode('utf-8').strip()
            if type not in list(set(cor.constants.genbank.TO_CORAL)):
                type = 'misc_feature'
            f = cor.Feature(name, start, stop, type, strand=strand, qualifiers=qualifiers)
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
            if sample_type['name'] not in ['Plasmid', 'Fragment']:
                raise BenchlingAPIException('Could not find Sequence in aquarium sample {}. \
                Sample is of sample type {} not a Fragment or Plasmid. \
                Error Message: {}'.format(sample_type['name'], sample['id'], e))
        return share_link

    def getAqSeq(self, value, query='id'):
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
        benchlingsequence = self.getSequenceFromShareLink(share_link)
        return self.convertToCoral(benchlingsequence)

    def _toCoralPrimer(self, aq_sample):
        anneal = cor.DNA(aq_sample['fields']['Anneal Sequence'].strip())
        overhang = cor.DNA(aq_sample['fields']['Overhang Sequence'].strip())
        tm = int(aq_sample['fields']['T Anneal'])
        return cor.Primer(anneal, tm, overhang)

    def getAqPrimer(self, value, query='id'):
        sample = self.AqAPI.find('sample', {query: value})['rows'][0]
        if sample['sample_type_id'] == 1:
            return self._toCoralPrimer(sample)
        else:
            raise ValueError("Sample is not a primer. Sample type id: {}".format(sample['sample_type_id']))

    def getAqFraq(self, frag_id, try_share_link = True):
        frag = self.AqAPI.find('sample', {'id': frag_id})['rows'][0]

        # Try share link
        if try_share_link:
            frag_link = frag['fields']['Sequence']
            if self._verifyShareLink(frag_link):
                return self.getSequenceFromShareLink(frag_link)

        # Get sequence from pcr
        template_name = frag['fields']['Template']
        template = self.AqAPI.find('sample', {'name': template_name})['rows'][0]
        link = template['fields']['Sequence']
        p1_name = frag['fields']['Forward Primer']
        p1 = self.AqAPI.find('sample', {'name': p1_name})['rows'][0]
        p2_name = frag['fields']['Reverse Primer']
        p2 = self.AqAPI.find('sample', {'name': p2_name})['rows'][0]
        template = self.convertToCoral(self.getSequenceFromShareLink(link))
        fwd_primer = cor.Primer(cor.DNA(p1['fields']['Anneal Sequence']), p1['fields']['T Anneal'], overhang=cor.DNA(p1['fields']['Overhang Sequence']))
        rev_primer = cor.Primer(cor.DNA(p2['fields']['Anneal Sequence']), p2['fields']['T Anneal'], overhang=cor.DNA(p2['fields']['Overhang Sequence']))
        pcr_result = cor.reaction.pcr(template, fwd_primer, rev_primer)

        return pcr_result, template

    def gibsonFromFrags(self, list_of_frag_ids, linear=False):
        frags = []
        for frag_id in list_of_frag_ids:
            frag, template = self.getAqFragmentSequence(frag_id)
            frags.append(frag)
        return cor.reaction.gibson(frags, linear=linear)

    def gibsonFromTask(self, task_id, linear=False):
        task = self.AqAPI.find('task', {'id': task_id})['rows'][0]
        specs = json.loads(task['specification'])
        frags = specs['fragments Fragment']
        return self.gibsonAssemblyFromAqFragments(frags, linear=linear)


    def getPrimerSequenceFromAquarium(self, value, query):
        pass

    def makeCoralDNA(self, sequence):
        pass
