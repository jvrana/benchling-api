from benchlingapi import BenchlingPortal
import coral as cor
import os
import subprocess
import tempfile


def openape(dna):
    tmp = tempfile.mkdtemp()
    filename = os.path.join(tmp, 'tmp.ape')
    cor.seqio.write_dna(dna, filename)
    subprocess.call(['open', '-a', 'ApE', filename])
# cor.seqio.read_dna('fragment-4256-pgadt7rec_ts-amp_split.gb')
# bench_api_key = 'sk_g7fo2vxkNUYNPkShOFIOmtY9ejIGE'
# aq_api_key = 'GwZdTb4jr8YL3wwmVi1QYfG6jeLzUYxkLSZ7BAIKnOc'
# aq_user = 'vrana'
# aq_url = 'http://54.68.9.194:81/api'
# credentials = [bench_api_key, aq_url, aq_user, aq_api_key]
# portal = BenchlingPortal(*credentials)
#
# frag4256 = portal.getAqSeq(4256)
# frag4257 = portal.getAqSeq(4257)
# cor.seqio.write_dna(frag4256, 'frag4256.gb')
# cor.seqio.read_dna('frag4256.gb')
# frag_list = [frag4256, frag4257]
# frag_list_copy = [frag4256.copy().reverse_complement(), frag4257.copy().reverse_complement()]
#
# r = cor.reaction.gibson(frag_list, linear=True)
# r2 = cor.reaction.gibson(frag_list_copy, linear=True)
#
# openape(r)
#
# openape(r2)

from nose.tools import assert_equal, assert_true, assert_raises

f1 = cor.seqio.read_dna('fragment-4256-pgadt7rec_ts-amp_split.gb')
f2 = cor.seqio.read_dna('fragment-4257-pgadt7rec_pp2_amp_split.gb')
f3 = f1.copy().reverse_complement()
f3.name = f3.name + " flipped"
f4 = f2.copy().reverse_complement()
f4.name = f4.name + " flipped"
expected = cor.seqio.read_dna('gibsonresult.gb')

gb = cor.reaction.gibson([f1, f2], linear=True)
gb_flipped = cor.reaction.gibson([f3, f4], linear=True)

# Ensure expected lengths are the same
assert_equal(len(expected), len(gb))

# Ensure gibson sequence is in expected sequence
fwd_loc, rev_loc = expected.locate(gb)
assert_true(rev_loc or fwd_loc)
fwd_loc, rev_loc = expected.locate(gb_flipped)
assert_true(fwd_loc or rev_loc)


def examine(result, expected, frag_list):
    f, r = expected.locate(result)
    if f:
        orientation = 1
    elif r:
        orientation = 0

    if not orientation:
        expected = expected.reverse_complement()


    assert_equal(len(result.features), len(expected.features))
    h = []
    for f in result.features:
        if not result.select_features(f.name)==expected.select_features(f.name):
            print result.select_features(f.name)
            print expected.select_features(f.name)
            pass
    for f in expected.features:
        if not result.select_features(f.name)==expected.select_features(f.name):
            print result.select_features(f.name)
            print expected.select_features(f.name)
            pass
    for f in expected.features:
        pass
    openape(result)
    openape(expected)
g1 = examine(gb, expected, [f1, f2])
g2 = examine(gb_flipped, expected, [f3, f4])