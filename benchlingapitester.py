# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 16:48:28 2015
Testing Gibson Assembly Reaction from Aquarium
@author: Justin
"""
from benchlingapi import BenchlingAPI, BenchlingPortal
import coral as cor
import subprocess

credentials = (
    'sk_g7fo2vxkNUYNPkShOFIOmtY9ejIGE',
    'http://54.68.9.194:81/api',
    'vrana',
    'GwZdTb4jr8YL3wwmVi1QYfG6jeLzUYxkLSZ7BAIKnOc')
portal = BenchlingPortal(*credentials)

def frag_seq(frag_id):
    frag = portal.AqAPI.find('sample', {'id': frag_id})['rows'][0]
    template_name = frag['fields']['Template']
    template = portal.AqAPI.find('sample', {'name': template_name})['rows'][0]
    link = template['fields']['Sequence']
    p1_name = frag['fields']['Forward Primer']
    p1 = portal.AqAPI.find('sample', {'name': p1_name})['rows'][0]
    p2_name = frag['fields']['Reverse Primer']
    p2 = portal.AqAPI.find('sample', {'name': p2_name})['rows'][0]
    template = portal.convertToCoral(portal.getSequenceFromShareLink(link))
    fwd_primer = cor.Primer(cor.DNA(p1['fields']['Anneal Sequence']), p1['fields']['T Anneal'], overhang=cor.DNA(p1['fields']['Overhang Sequence']))
    rev_primer = cor.Primer(cor.DNA(p2['fields']['Anneal Sequence']), p2['fields']['T Anneal'], overhang=cor.DNA(p2['fields']['Overhang Sequence']))
    pcr_result = cor.reaction.pcr(template, fwd_primer, rev_primer)
    return pcr_result, template

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

result = cor.reaction.gibson(frags, linear=False)

cor.seqio.write_dna(result, 'plasmid.gb')
subprocess.call(['open', '-a', 'ApE (Mavericks)', 'plasmid.gb'])
