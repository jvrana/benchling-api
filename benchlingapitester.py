# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 16:48:28 2015

@author: Justin
"""
import requests
import json
import os
from urllib2 import urlopen
from bs4 import BeautifulSoup
import re
import coral as cor
from aquariumapi import AquariumAPI
import subprocess

production_api = AquariumAPI(
    "http://54.68.9.194:81/api",
    'vrana',
    'GwZdTb4jr8YL3wwmVi1QYfG6jeLzUYxkLSZ7BAIKnOc')
Aq = production_api

bench_api = 'sk_g7fo2vxkNUYNPkShOFIOmtY9ejIGE'


# Benchling API Info: https://api.benchling.com/docs/#sequence-sequence-collections-post
class Benchling_API(object):
    
    def __init__(self, api_key):
        self.home = 'https://api.benchling.com/v1/'
        self.auth = (api_key, '')  
        self.seq_dict = {} #seq_name: seq_information
        self.folder_dict = {} #folder_name: fodler_information
        
    def _post(self, payload):        
        pass
    
    def _get(self, what):
        print "\tCall:", what
        r = requests.get(os.path.join(self.home, what), auth=self.auth)
        d = json.loads(r.text)
        print "\tResponse:", r
        return d
    
    def getNameFromLink(self, share_link):
        ''' A really hacky way to get a sequence 
        name from a Benchling share link
        '''
        f = urlopen(share_link)
        soup = BeautifulSoup(f.read())
        title = soup.title.text
        gp = re.search("(.+)\s.\sBenchling", title)
        return gp.group(1)
    
    def getSeqFromLink(self, share_link):
        name = self.getNameFromLink(share_link)
        return self.getSequence(name)
    
    def createDictionaries(self):
        self.folders = self._get('folders')['folders']
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
                
    def getSequence(self, value, query='name'):
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
            print a
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
        
        
    
    def makeCoralDNA(self, sequence):
        pass
            
api = Benchling_API(bench_api)
api.createDictionaries()
s = api.getSeqFromLink('https://benchling.com/s/kOXp01qQ/edit')
c = api.convertToCoral(s)

p1 = cor.Primer(cor.DNA('ATGGACTACAAAGACGATGACGACAAG'), 61.1)
p2 = cor.Primer(cor.DNA('TTAACAATTAATTAACATATCGAGATCGAAATCGTCCAG'), 62.2)

pcr = cor.reaction.pcr(c, p1, p2)

def frag_seq(frag_id):
    global frags
    #print "Fragment", frag_id
    frag = Aq.find('sample', {'id': frag_id})['rows'][0]
    #print "\tFinding fragment with id {}.".format(frag_id)
    template_name = frag['fields']['Template']
    template = Aq.find('sample', {'name': template_name})['rows'][0]
    #print "\tFinding template with sample name {}.".format(template_name)
    link = template['fields']['Sequence']
    #print "\tGetting link to sequence: {}".format(link)
    p1_name = frag['fields']['Forward Primer']
    p1 = Aq.find('sample', {'name': p1_name})['rows'][0]
    p2_name = frag['fields']['Reverse Primer']
    p2 = Aq.find('sample', {'name': p2_name})['rows'][0]
    try:
        print 'before pcr',
        print frags[0].features[0].qualifiers
    except:
        pass
    template = api.convertToCoral(api.getSeqFromLink(link))
    try:
        print 'after api.convertToCoral',
        print frags[0].features[0].qualifiers
    except:
        pass
    #cor.seqio.write_dna(template, "{}.gb".format(template_name))
    try:
        print 'after coral.seqio.write_dna',
        print frags[0].features[0].qualifiers
    except:
        pass
    fwd_primer = cor.Primer(cor.DNA(p1['fields']['Anneal Sequence']), p1['fields']['T Anneal'], overhang=cor.DNA(p1['fields']['Overhang Sequence']))
    rev_primer = cor.Primer(cor.DNA(p2['fields']['Anneal Sequence']), p2['fields']['T Anneal'], overhang=cor.DNA(p2['fields']['Overhang Sequence']))
    pcr_result = cor.reaction.pcr(template, fwd_primer, rev_primer)
    try:
        print 'after pcr',
        print frags[0].features[0].qualifiers
    except:
        pass
    return pcr_result, template

def process_feature_type(feature_type, bio_to_coral=True):
    '''Translate genbank feature types into usable ones (currently identical).
    The feature table is derived from the official genbank spec (gbrel.txt)
    available at http://www.insdc.org/documents/feature-table

    :param feature_type: feature to convert
    :type feature_type: str
    :param bio_to_coral: from coral to Biopython (True) or the other direction
                   (False)
    :param bio_to_coral: bool
    :returns: coral version of genbank feature_type, or vice-versa.
    :rtype: str

    '''

    err_msg = 'Unrecognized feature type: {}'.format(feature_type)
    if bio_to_coral:
        try:
            name = coral.constants.genbank.TO_CORAL[feature_type]
        except KeyError:
            raise ValueError(err_msg)
    else:
        try:
            name = cor.constants.genbank.TO_BIO[feature_type]
        except KeyError:
            raise ValueError(err_msg)
    return name


def coral_to_seqfeature(feature):
    '''Convert a coral.Feature to a Biopython SeqFeature.

    :param feature: coral Feature.
    :type feature: coral.Feature

    '''
    global frags
    bio_strand = 1 if feature.strand == 1 else -1
    ftype = process_feature_type(feature.feature_type, bio_to_coral=False)
    sublocations = []
    if feature.gaps:
        # There are gaps. Have to define location_operator and  add subfeatures
        location_operator = 'join'
        # Feature location means nothing for 'join' sequences?
        # TODO: verify
        location = FeatureLocation(ExactPosition(0), ExactPosition(1),
                                   strand=bio_strand)
        # Reconstruct start/stop indices for each subfeature
        stops, starts = zip(*feature.gaps)
        starts = [feature.start] + [start + feature.start for start in starts]
        stops = [stop + feature.start for stop in stops] + [feature.stop]
        # Build subfeatures
        for start, stop in zip(starts, stops):
            sublocation = FeatureLocation(ExactPosition(start),
                                          ExactPosition(stop),
                                          strand=bio_strand)
            sublocations.append(sublocation)
        location = CompoundLocation(sublocations, operator='join')
    else:
        # No gaps, feature is simple
        location_operator = ''
        location = FeatureLocation(ExactPosition(feature.start),
                                   ExactPosition(feature.stop),
                                   strand=bio_strand)
    qualifiers = feature.qualifiers.copy()
    qualifiers['label'] = [feature.name]
    seqfeature = SeqFeature(location, type=ftype,
                            qualifiers=qualifiers,
                            location_operator=location_operator)
    return seqfeature    

#print coral_to_seqfeature(frags[0].features[0])
#f1 = coral_to_seqfeature(frags[0].features[0])
#print f1
#print coral_to_seqfeature(frags[0].features[1])
#f2 = coral_to_seqfeature(frags[0].features[1])
#print f2
#coral_to_seqfeature(frags[1].features[2])
#features = [f1, f2]
#print features[0]
#print features[1]
#
#SeqFeature(qualifiers={'label': 'ok'})
#print features[0]
#print features[1]

frags = []

for f in [4257, 4256, 11222]:
    print "Collecting fragment {}".format(f)
    frag, template = frag_seq(f)
    print "pcr features:", frag.features[0].qualifiers
    frags.append(frag)
    print 'frag[0]:', frags[0].features[0].qualifiers
    filename = str(f) + '.gb'
    #cor.seqio.write_dna(frag, filename)
    subprocess.call(['open', '-a', 'ApE (Mavericks)', filename])


#print "Performing Gibson"
result = cor.reaction.gibson(frags, linear=False)
#annotated_features = []
#for fragment in frags:
#    for feature in fragment.features:
#        print feature
#        feature_seq = fragment.extract(feature)
#        loc = result.locate(feature_seq)
#        print loc
#        #print feature_seq
#        print
#        length = abs(feature.start - feature.stop)
#        fwd_binding = loc[0]
#        rev_binding = loc[1]
#        for site in fwd_binding:
#            start = site
#            stop = site + length
#            f = (start, stop)
#            if f not in annotated_features:
#                annotated_features.append(f)
#                new_feature = feature.copy()
#                new_feature.start = start
#                new_feature.stop = stop
#                result.features.append(new_feature)
cor.seqio.write_dna(result, 'plasmid.gb')
subprocess.call(['open', '-a', 'ApE (Mavericks)', 'plasmid.gb'])