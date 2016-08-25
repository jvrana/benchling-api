from Bio import SeqIO
from Bio.SeqFeature import *
from Bio.SeqIO import *
from Bio.Seq import *
from Bio.Alphabet import generic_dna
import copy


def encode_dictionary(dictionary):
    for key in dictionary:
        if isinstance(dictionary[key], unicode):
            dictionary[key] = dictionary[key].encode('utf-8')
        elif isinstance(dictionary[key], dict):
            encode_dictionary(dictionary[key])
    return


def _convert_benchling_features(benchling_seq):
    seqfeatures = []
    for ftr in benchling_seq['annotations']:
        info = \
            dict(location=FeatureLocation(ftr['start'], ftr['end']), type=ftr['type'], strand=ftr['strand'],
                 id=ftr['name'], qualifiers={
                    'label': ftr['name'],
                    'ApEinfo_fwdcolor': ftr['color'],
                    'ApEinfo_revcolor': ftr['color'],
                    'color': ftr['color']
                })
        if info['type'].strip() == '':
            info['type'] = 'misc'
        info = copy.deepcopy(info)
        encode_dictionary(info)
        seqfeature = SeqFeature(**info)
        seqfeatures.append(seqfeature)
    return seqfeatures


def benchling_to_seqrecord(benchling_seq):
    bseq = benchling_seq
    features = _convert_benchling_features(bseq)
    seq = Seq(bseq['bases'], generic_dna)
    kwargs = {
        'description': '\n'.join([bseq['name'], bseq['description']]),
        'dbxrefs': bseq['aliases'],
        'features': features,
        'annotations': {'full_name': bseq['name'].encode('utf-8')},
        'letter_annotations': None,
        'name': str(bseq['name'][:10]),
        'id': bseq['id']
    }
    kwargs = copy.deepcopy(kwargs)
    encode_dictionary(kwargs)
    for key in kwargs:
        if isinstance(kwargs[key], unicode):
            kwargs[key] = kwargs[key].encode('utf-8')
    return SeqRecord(seq, **kwargs)


def write_to_gb(seqrecord, filename):
    with open(filename, 'w') as handle:
        SeqIO.write(seqrecord, handle, 'genbank')
        handle.close()
