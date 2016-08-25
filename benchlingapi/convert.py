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

def _clean_seqrecord_features(seqrecord):
    for f in seqrecord.features:
        if f.type.strip() == '':
            f.type = 'misc'

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
    seqrec = SeqRecord(seq, **kwargs)
    _clean_seqrecord_features(seqrec)
    return seqrec


def write_to_gb(seqrecord, filename):
    with open(filename, 'w') as handle:
        SeqIO.write(seqrecord, handle, 'genbank')
        handle.close()


def _get_benchlingfeatures_from_seqrecord(seqrec):
    annotations = []
    for feature in seqrec.features:
        location = feature.location
        qualifiers = feature.qualifiers

        start = location.start.position
        end = location.end.position
        type = feature.type
        strand = feature.strand
        if strand not in [-1, 1]:
            strand = 1
        try:
            name = qualifiers['label']
        except:
            name = 'unlabeled'
        try:
            color = qualifiers['color']
        except:
            color = '#F58A5E'

        annotation = {
            'start': start,
            'end': end,
            'type': type,
            'strand': strand,
            'name': name,
            'color': color
        }
        annotations.append(annotation)
    return annotations

def _seqrecord_to_benchling(seqrec, default_circular=True):
    seqrec = copy.deepcopy(seqrec)
    _clean_seqrecord_features(seqrec)
    annotations = _get_benchlingfeatures_from_seqrecord(seqrec)
    bases = seqrec.seq.tostring()
    circular = default_circular
    assert isinstance(default_circular, bool)
    try:
        circular = seqrec.circular
    except:
        print "Could not determine topology, defaulted to {}".format(default_circular)
        pass
    # force with argument
    aliases = seqrec.dbxrefs
    description = seqrec.description
    folder = 'argument'
    name = seqrec.name
    try:
        seqrec.annotations['full_name']
    except:
        pass
    bseq_id = seqrec.id # add to aliases?
    aliases.append(bseq_id)
    aliases = list(set(aliases))
    bseq = dict(
        annotations=annotations,
        description=description,
        folder=None,
        aliases=aliases,
        bases=bases,
        circular=circular,
        name=name
    )
    return bseq

def save_seqrecord_to_benchling(seqrec, folder, api):
    bseq = _seqrecord_to_benchling(seqrec)
    bseq['folder'] = folder
    api._post('sequences/', bseq)