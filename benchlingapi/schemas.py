from marshmallow import Schema, fields, pprint, post_load

from benchlingapi.models import Sequence, Folder, Annotation, Primer, Entity


class PermissionsSchema(Schema):
    admin = fields.Boolean()
    owner = fields.Boolean()
    readable = fields.Boolean()
    writable = fields.Boolean()
    appendable = fields.Boolean()


class EntitySchema(Schema):
    id = fields.String()
    avatarUrl = fields.URL()
    handle = fields.String()
    name = fields.String()
    type = fields.String()
    website = fields.String()
    location = fields.String()
    joined_on = fields.DateTime()

    @post_load
    def make(self, data):
        return Entity(**data)


class TagSchema(Schema):
    name = fields.String()
    value = fields.String(many=True)
    url = fields.URL()
    reference = fields.String()


class PrimerSchema(Schema):
    name = fields.String()
    bases = fields.String()
    color = fields.String()
    start = fields.Integer()
    end = fields.Integer()
    overhang_length = fields.Integer()
    strand = fields.Integer()
    created_at = fields.DateTime()
    bind_position = fields.Integer()

    @post_load
    def make(self, data):
        return Primer(**data)


class AnnotationSchema(Schema):
    name = fields.String()
    strand = fields.Integer()
    color = fields.String()
    type = fields.String()
    start = fields.Integer()
    end = fields.Integer()

    @post_load
    def make(self, data):
        return Annotation(**data)


class SequenceSchema(Schema):
    aliases = fields.List(fields.String)
    created_at = fields.Time()
    modified_at = fields.Time()
    creator = fields.Nested("EntitySchema")
    folder = fields.Nested("FolderSchema")
    name = fields.String()
    tags = fields.Nested("TagSchema", many=True)
    id = fields.String()
    editURL = fields.String()
    circular = fields.Boolean()
    length = fields.Integer()
    description = fields.String()
    bases = fields.String()
    annotations = fields.Nested("AnnotationSchema", many=True)
    primers = fields.Nested("PrimerSchema", many=True)
    color = fields.String()

    @post_load
    def make(self, data):
        return Sequence(**data)


class FolderSchema(Schema):
    id = fields.String()
    name = fields.Str()
    description = fields.Str()
    owner = fields.Str()
    permissions = fields.Nested(PermissionsSchema)
    type = fields.Str()
    count = fields.Integer()
    created_at = fields.String()
    modified_at = fields.String()
    sequences = fields.Nested("SequenceSchema", many=True)

    @post_load
    def make(self, data):
        return Folder(**data)


class ProteinSchema(Schema):
    aliases = fields.String(many=True)
    aminoAcids = fields.String()
    annotations = fields.Nested("AnnotationSchema", many=True)
    tags = fields.Nested("TagSchema", many=True)
    folder = fields.String()
    name = fields.String()


seq = {'aliases': [],
       'annotations': [{'color': '#FF9CCD',
                        'end': 3877,
                        'name': '1045',
                        'start': 3838,
                        'strand': -1,
                        'type': 'primer_bind'},
                       {'color': '#FF9CCD',
                        'end': 3877,
                        'name': '1590 (ADH1 + tTRP1_Rev)',
                        'start': 3839,
                        'strand': -1,
                        'type': 'primer_bind'},
                       {'color': '#F58A5E',
                        'end': 22,
                        'name': 'TS',
                        'start': 0,
                        'strand': 1,
                        'type': 'site'},
                       {'color': '#85DAE9',
                        'end': 3877,
                        'name': "TRP1 3' UTR",
                        'start': 3831,
                        'strand': 1,
                        'type': 'terminator'},
                       {'color': '#85DAE9',
                        'end': 4873,
                        'name': 'Differs from Gottschling map',
                        'start': 4872,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#F58A5E',
                        'end': 5140,
                        'name': 'Differs from Gottschling Map',
                        'start': 5139,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#B1FF67',
                        'end': 6040,
                        'name': 'EYFP',
                        'start': 5332,
                        'strand': 1,
                        'type': 'gene'},
                       {'color': '#d03bff',
                        'end': 4534,
                        'name': 'GAL1',
                        'start': 4083,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#85DAE9',
                        'end': 4591,
                        'name': 'TC In Frame',
                        'start': 4589,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#85DAE9',
                        'end': 6311,
                        'name': 'CYC1_terminator',
                        'start': 6071,
                        'strand': 1,
                        'type': 'terminator'},
                       {'color': '#B1FF67',
                        'end': 5278,
                        'name': 'L2',
                        'start': 5248,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#e14c73',
                        'end': 5041,
                        'name': 'IAA17 +202 to +333',
                        'start': 4909,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#cb4b2c',
                        'end': 4059,
                        'name': 'ADH1',
                        'start': 3877,
                        'strand': 1,
                        'type': 'terminator'},
                       {'color': '#FF9CCD',
                        'end': 3877,
                        'name': "1589 (tTRP1 3'UTR + tADH1_Fwd)",
                        'start': 3864,
                        'strand': 1,
                        'type': 'primer_bind'},
                       {'color': '#85DAE9',
                        'end': 6049,
                        'name': 'Stop Codon',
                        'start': 6046,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#004c4c',
                        'end': 2897,
                        'name': 'Amp and ori',
                        'start': 485,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#85DAE9',
                        'end': 3156,
                        'name': "TRP1 5' UTR",
                        'start': 2905,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#FFEF86',
                        'end': 6046,
                        'name': 'ORF frame 2',
                        'start': 5332,
                        'strand': -1,
                        'type': 'CDS'},
                       {'color': '#FF9CCD',
                        'end': 4059,
                        'name': '1560',
                        'start': 4031,
                        'strand': -1,
                        'type': 'primer_bind'},
                       {'color': '#C7B0E3',
                        'end': 4565,
                        'name': 'attR1',
                        'start': 4564,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#F58A5E',
                        'end': 2511,
                        'name': 'Ampicillin',
                        'start': 1650,
                        'strand': -1,
                        'type': 'CDS'},
                       {'color': '#85DAE9',
                        'end': 4557,
                        'name': 'pBluescriptSK_Primer',
                        'start': 4540,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#FF9CCD',
                        'end': 3924,
                        'name': "1589 (tTRP1 3'UTR + tADH1_Fwd)",
                        'start': 3877,
                        'strand': 1,
                        'type': 'primer_bind'},
                       {'color': '#84B0DC',
                        'end': 3877,
                        'name': 'New Feature',
                        'start': 2905,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#6c59ff',
                        'end': 5044,
                        'name': 'Extra serine, shared by VP16/hER',
                        'start': 5041,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#a17689',
                        'end': 3059,
                        'name': 'Fill-in removed EcoRI',
                        'start': 3049,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#9EAFD2',
                        'end': 6004,
                        'name': 'EGFP_C_primer',
                        'start': 5982,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#ff3e3e',
                        'end': 2581,
                        'name': 'AmpR_promoter',
                        'start': 2552,
                        'strand': -1,
                        'type': 'promoter'},
                       {'color': '#F58A5E',
                        'end': 6071,
                        'name': 'TP',
                        'start': 6049,
                        'strand': 1,
                        'type': 'site'},
                       {'color': '#B1FF67',
                        'end': 4872,
                        'name': 'GAL4(1-93) DBD',
                        'start': 4594,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#B1FF67',
                        'end': 2905,
                        'name': 'PmeI site',
                        'start': 2897,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#B1FF67',
                        'end': 485,
                        'name': 'PmeI site',
                        'start': 477,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#ff0000',
                        'end': 4589,
                        'name': 'attB1',
                        'start': 4565,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#84B0DC',
                        'end': 4059,
                        'name': 'New Feature',
                        'start': 3877,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#FFEF86',
                        'end': 2511,
                        'name': 'Ampicillin',
                        'start': 1650,
                        'strand': -1,
                        'type': 'gene'},
                       {'color': '#FF9CCD',
                        'end': 1496,
                        'name': 'pBR322_origin',
                        'start': 876,
                        'strand': -1,
                        'type': 'rep_origin'},
                       {'color': '#FFEF86',
                        'end': 6046,
                        'name': 'EYFP',
                        'start': 5332,
                        'strand': 1,
                        'type': 'CDS'},
                       {'color': '#B1FF67',
                        'end': 3831,
                        'name': 'TRP1',
                        'start': 3156,
                        'strand': 1,
                        'type': 'gene'},
                       {'color': '#0063ff',
                        'end': 477,
                        'name': "TRP1 3' UTR extended",
                        'start': 22,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#9EAFD2',
                        'end': 5396,
                        'name': 'EGFP_N_primer',
                        'start': 5374,
                        'strand': -1,
                        'type': 'misc_feature'},
                       {'color': '#F58A5E',
                        'end': 4083,
                        'name': 'PP2',
                        'start': 4059,
                        'strand': 1,
                        'type': 'site'},
                       {'color': '#FF9CCD',
                        'end': 3899,
                        'name': '1590 (ADH1 + tTRP1_Rev)',
                        'start': 3877,
                        'strand': -1,
                        'type': 'primer_bind'},
                       {'color': '#85DAE9',
                        'end': 5248,
                        'name': 'HSV1 VP16',
                        'start': 5044,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#000eff',
                        'end': 4594,
                        'name': 'Yeast Kozak',
                        'start': 4591,
                        'strand': 1,
                        'type': 'misc_feature'},
                       {'color': '#0d16ff',
                        'end': 5320,
                        'name': 'Double SV40',
                        'start': 5278,
                        'strand': 1,
                        'type': 'misc_feature'}],
       'bases': 'atgtcgtaataaccccgccccgtgcaggccttttgaaaagcaagcataaaagatctaaacataaaatctgtaaaataacaagatgtaaagataatgctaaatcatttggctttttgattgattgtacaggaaaatatacatcgcagggggttgacttttaccatttcaccgcaatggaatcaaacttgttgaagagaatgttcacaggcgcatacgctacaatgacccgattcttgctagccttttctcggtcttgcaaacaaccgccggcagcttagtatataaatacacatgtacatacctctctccgtatcctcgtaatcattttcttgtatttatcgtcttttcgctgtaaaaactttatcacacttatctcaaatacacttattaaccgcttttactattatcttctacgctgacagtaatatcaaacagtgacacatattaaacacagtggtttctttgcataaacaccatgtttaaaccatggtcatagctgtttcctgtgtgaaattgttatccgctcacaattccacacaacataggagccggaagcataaagtgtaaagcctggggtgcctaatgagtgaggtaactcacattaattgcgttgcgctcactgcccgctttccagtcgggaaacctgtcgtgccagctgcattaatgaatcggccaacgcgcggggagaggcggtttgcgtattgggcgctcttccgcttcctcgctcactgactcgctgcgctcggtcgttcggctgcggcgagcggtatcagctcactcaaaggcggtaatacggttatccacagaatcaggggataacgcaggaaagaacatgtgagcaaaaggccagcaaaaggccaggaaccgtaaaaaggccgcgttgctggcgtttttccataggctcggcccccctgacgagcatcacaaaaatcgacgctcaagtcagaggtggcgaaacccgacaggactataaagataccaggcgttcccccctggaagctccctcgtgcgctctcctgttccgaccctgccgcttaccggatacctgtccgcctttctcccttcgggaagcgtggcgctttctcaatgctcacgctgtaggtatctcagttcggtgtaggtcgttcgctccaagctgggctgtgtgcacgaaccccccgttcagcccgaccgctgcgccttatccggtaactatcgtcttgagtccaacccggtaagacacgacttatcgccactggcagcagccactggtaacaggattagcagagcgaggtatgtaggcggtgctacagagttcttgaagtggtggcctaactacggctacactagaaggacagtatttggtatctgcgctctgctgaagccagttaccttcggaaaaagagttggtagctcttgatccggcaaacaaaccaccgctggtagcggtggtttttttgtttgcaagcagcagattacgcgcagaaaaaaaggatctcaagaagatcctttgatcttttctacggggtctgacgctcagtggaacgaaaactcacgttaagggattttggtcatgagattatcaaaaaggatcttcacctagatccttttaaattaaaaatgaagttttaaatcaatctaaagtatatatgagtaaacttggtctgacagttaccaatgcttaatcagtgaggcacctatctcagcgatctgtctatttcgttcatccatagttgcctgactgcccgtcgtgtagataactacgatacgggagggcttaccatctggccccagtgctgcaatgataccgcgagacccacgctcaccggctccagatttatcagcaataaaccagccagccggaagggccgagcgcagaagtggtcctgcaactttatccgcctccatccagtctattaattgttgccgggaagctagagtaagtagttcgccagttaatagtttgcgcaacgttgttgccattgctacaggcatcgtggtgtcacgctcgtcgtttggtatggcttcattcagctccggttcccaacgatcaaggcgagttacatgatcccccatgttgtgaaaaaaagcggttagctccttcggtcctccgatcgttgtcagaagtaagttggccgcagtgttatcactcatggttatggcagcactgcataattctcttactgtcatgccatccgtaagatgcttttctgtgactggtgagtactcaaccaagtcattctgagaatagtgtatgcggcgaccgagttgctcttgcccggcgtcaatacgggataataccgcgccacatagcagaactttaaaagtgctcatcattggaaaacgttcttcggggcgaaaactctcaaggatcttaccgctgttgagatccagttcgatgtaacccactcgtgcacccaactgatcttcagcatcttttactttcaccagcgtttctgggtgagcaaaaacaggaaggcaaaatgccgcaaaaaagggaataagggcgacacggaaatgttgaatactcatactcttcctttttcaatattattgaagcatttatcagggttattgtctcatgagcggatacatatttgaatgtatttagaaaaataaacaaataggggttccgcgcacatttccccgaaaagtgccacctgacgtctaagaaaccattattatcatgacattaacctataaaaataggcgtatcacgaggccctttcgtctcgcgcgtttcggtgatgacggtgaaaacctctgacacatgcagctcccggagacggtcacagcttgtctgtaagcggatgccgggagcagacaagcccgtcagggcgcgtcagcgggtgttggcgggtgtcggggctggcttaactatgcggcatcagagcagattgtactgagagtgcaccatagtttaaaccatttaatagaacagcatcgtaatatatgtgtactttgcagttatgacgccagatggcagtagtggaagatattctttattgaaaaatagcttgtcaccttacgtacaatcttgatccggagcttttctttttttgccgattaagaattaattcggtcgaaaaaagaaaaggagagggccaagagggagggcattggtgactattgagcacgtgagtatacgtgattaagcacacaaaggcagcttggagtatgtctgttattaatttcacaggtagttctggtccattggtgaaagtttgcggcttgcagagcacagaggccgcagaatgtgctctagattccgatgctgacttgctgggtattatatgtgtgcccaatagaaagagaacaattgacccggttattgcaaggaaaatttcaagtcttgtaaaagcatataaaaatagttcaggcactccgaaatacttggttggcgtgtttcgtaatcaacctaaggaggatgttttggctctggtcaatgattacggcattgatatcgtccaactgcatggagatgagtcgtggcaagaataccaagagttcctcggtttgccagttattaaaagactcgtatttccaaaagactgcaacatactactcagtgcagcttcacagaaacctcattcgtttattcccttgtttgattcagaagcaggtgggacaggtgaacttttggattggaactcgatttctgactgggttggaaggcaagagagccccgaaagcttacattttatgttagctggtggactgacgccagaaaatgttggtgatgcgcttagattaaatggcgttattggtgttgatgtaagcggaggtgtggagacaaatggtgtaaaagactctaacaaaatagcaaatttcgtcaaaaatgctaagaaataggttattactgagtagtatttatttaagtattgtttgtgcacttgccgcgaatttcttatgatttatgatttttattattaaataagttataaaaaaaataagtgtatacaaattttaaagtgactcttaggttttaaaacgaaaattcttattcttgagtaactctttcctgtaggtcaggttgctttctcaggtatagcatgaggtcgctcttattgaccacacctcccttaaccagattcgaaaagcggcacggattagaagccgccgagCGGGTGACAGCCCTCCGAAGGAAGACTCTCCTCCGTGCGTCCTCGTCTTCACCGGTCGCGTTCCTGAAACGCAGATGTGCCTCGCGCCGCACTGCTCCGAACAATAAAGATTCTACAATACTAGCTTTTATGGTTATGAAGAGGAAAAATTGGCAGTAACCTGGCCCCACAAACCTTCAAATGAACGAATCAAATTAACAACCATAGGATGATAATGCGATTAGTTTTTTAGCCTTATTTCTGGGGTAATTAATCAGCGAAGCGATGATTTTTGATCTATTAACAGATATATAAATGCAAAAACTGCATAACCACTTTAACTAATACTTTCAACATTTTCGGTTTGTATTACTTCTTATTCAAATGTAATAAAAGTATCAACAAAAAATTGTTAATATACCTCTATACTTTAACGTCAAGGAGaaaaaaccccggattctagaactagtggatcccccatcaCAAGTTTGTACAAAAAAGCAGGCTTCAAAATGAAGCTACTGTCTTCTATCGAACAAGCATGCGATATTTGCCGACTTAAAAAGCTCAAGTGCTCCAAAGAAAAACCGAAGTGCGCCAAGTGTCTGAAGAACAACTGGGAGTGTCGCTACTCTCCCAAAACCAAAAGGTCTCCGCTGACTAGGGCACATCTGACAGAAGTGGAATCAAGGCTAGAAAGACTGGAACAGCTATTTCTACTGATTTTTCCTCGAGAAGACCTTGACATGATTTTGAAAATGGATTCTTTACAGGATATAAAAGCATTGTTGggtacccctgcagctgcgtcgactctagaggatccaAGTGCTTGTCCTAAAGATCCAGCCAAACCTCCGGCCAAGGCACAAGTTGTGGGATGGCCACCGGTGAGATCATACCGGAAGAACGTGATGGTTTCCTGCCAAAAATCAAGCGGTGGCCCGGAGGCGGCGGCGtcggagctccacttagacggcgaggacgtggcgatggcgcatgccgacgcgctagacgatttcgatctggacatgttgggggacggggattccccgggtccgggatttaccccccacgactccgccccctacggcgctctggatatggccgacttcgagtttgagcagatgtttaccgatgcccttggaattgacgagtacggtgggggatccggttccggaagtggatccggatccCCCAAGAAGAAAAGAAAGGTCCCTAAAAAGAAACGTAAGGTTGGTGCTGGCGCCgtgagcaagggcgaggagctgttcaccggggtggtgcccatcctggtcgagctggacggcgacgtaaacggccacaagttcagcgtgtccggcgagggcgagggcgatgccacctacggcaagctgaccctgaagttcatctgcaccaccggcaagctgcccgtgccctggcccaccctcgtgaccaccttcggctacggcctgcagtgcttcgcccgctaccccgaccacatgaagcagcacgacttcttcaagtccgccatgcccgaaggctacgtccaggagcgcaccatcttcttcaaggacgacggcaactacaagacccgcgccgaggtgaagttcgagggcgacaccctggtgaaccgcatcgagctgaagggcatcgacttcaaggaggacggcaacatcctggggcacaagctggagtacaactacaacagccacaacgtctatatcatggccgacaagcagaagaacggcatcaaggtgaacttcaagatccgccacaacatcgaggacggcagcgtgcagctcgccgaccactaccagcagaacacccccatcggcgacggccccgtgctgctgcccgacaaccactacctgagctaccagtccgccctgagcaaagaccccaacgagaagcgcgatcacatggtcctgctggagttcgtgaccgccgccgggatcactctcggcatggacgagctgtacaagtaatgataccgtcgacctcgagtcaattagttatgtcacgcttacattcacgccctccccccacatccgctctaaccgaaaaggaaggagttagacaacctgaagtctaggtccctatttatttttttatagttatgttagtattaagaacgttatttatatttcaaatttttcttttttttctgtacagacgcgtgtacgcatgtaacattatactgaaaaccttgcttgagaaggttttgggacgctcgaaggctttaatttg',
       'circular': True,
       'color': '#F7977A',
       'createdAt': '2015-10-02T17:06:12.062561+00:00',
       'creator': {
           'avatarUrl': 'https://main-benchling.s3.amazonaws.com/a/uTfMphp2waolQNTz7pCpuIyPuAS1VLgVRlvMBwYS/ent_A7BlnCcJTU-sunshineyyy-128.png',
           'handle': 'sunshineyyy',
           'id': 'ent_A7BlnCcJTU',
           'name': 'Yaoyu Yang'},
       'description': 'pGAL1 drive GAVNY with potential workable linker between them '
                      '(pBluescriptSK + attB1) on TRP locus with TRP marker.',
       'editURL': '/sunshineyyy/f/pP6d50rJn1-plasmids/seq-0FmHFzJe-pmodt4-pgal1-attb1-gavny/edit',
       'folder': {'id': 'lib_pP6d50rJn1', 'name': 'Plasmids'},
       'id': 'seq_0FmHFzJe',
       'length': 6311,
       'modifiedAt': '2015-10-08T18:02:51.961487+00:00',
       'name': 'pMODT4-pGAL1-attB1-GAVNY',
       'notes': [{'created_at': '2015-10-08T18:02:51.961487+00:00',
                  'creator': 'ent_A7BlnCcJTU',
                  'text': ''},
                 {'created_at': '2015-10-08T18:02:51.961487+00:00',
                  'creator': 'ent_A7BlnCcJTU',
                  'text': ''},
                 {'created_at': '2015-10-08T18:02:51.961487+00:00',
                  'creator': 'ent_A7BlnCcJTU',
                  'text': ''},
                 {'created_at': '2015-10-08T18:02:51.961487+00:00',
                  'creator': 'ent_A7BlnCcJTU',
                  'text': ''}],
       'primers': [{'bases': 'tgactcgaggtcgacggtatca',
                    'bind_position': 6049,
                    'color': '#C6C9D1',
                    'created_at': '2015-10-02T17:15:26.143628+00:00',
                    'end': 6071,
                    'name': 'TP_rev',
                    'overhang_length': 0,
                    'start': 6049,
                    'strand': -1},
                   {'bases': 'AAGTTTGTACAAAAAAGCAGGCTTCAAAATGAAGCTACTGTCTTCTATCGAACAAGCATG',
                    'bind_position': 4625,
                    'color': '#FAAC61',
                    'created_at': '2015-10-02T17:14:43.317427+00:00',
                    'end': 4626,
                    'name': 'GAL4DBD_fwd_flk_attB1',
                    'overhang_length': 0,
                    'start': 4566,
                    'strand': 1}],
       'registryId': None,
       'tagSchema': None,
       'tags': []}

folder = {'count': 59, 'created_at': '2013-10-01T20:07:18+00:00', 'description': '', 'id': 'lib_pP6d50rJn1',
          'modified_at': '2017-01-20T21:57:55.991758+00:00', 'name': 'Plasmids', 'owner': 'ent_A7BlnCcJTU',
          'permissions': {'admin': True, 'appendable': True, 'owner': False, 'readable': True, 'writable': True},
          'sequences': [{'id': 'seq_ri07UntS', 'name': 'pMODU6-pGPD-EYFP'},
                        {'id': 'seq_2MFFshfl', 'name': 'pYMOD2Kmx_pGAL1-HYG_ZEV4-cassette'},
                        {'id': 'seq_ztl4dnOW', 'name': 'pLAB1'},
                        {'id': 'seq_vA5dxrqd', 'name': 'pMODU6-pGALZ4-AlphaFactor'},
                        {'id': 'seq_okitCPyx', 'name': 'pGPT4-pGAL1-GAVNY(VP64)'},
                        {'id': 'seq_7yXay7Ep', 'name': 'pGP8G-TIR1-Y'},
                        {'id': 'seq_7O7ThYSI', 'name': 'pMODU6-pGALZ4-Z4AVNY'},
                        {'id': 'seq_t77GYXRB', 'name': 'pGPT4-pGAL1-EGFP'},
                        {'id': 'seq_mfMW58Dd', 'name': 'pGPL5G-pGALZ4-URA3'},
                        {'id': 'seq_beOWphBv', 'name': 'pMODKan-HO-pACT1-ZEV4'},
                        {'id': 'seq_0FmHFzJe', 'name': 'pMODT4-pGAL1-attB1-GAVNY'},
                        {'id': 'seq_Nv6wYspV', 'name': 'FAR1-mut-87aa-TP'},
                        {'id': 'seq_5bmPzcKN', 'name': 'pMODU6-pGALZ4-NatMX'},
                        {'id': 'seq_f4GgnFdY', 'name': 'pGPT4-pGAL1-GAVNY_seq_verified'},
                        {'id': 'seq_QteKmJdS', 'name': 'pGPT4-pGAL1-GAVNY_mutated_library'},
                        {'id': 'seq_5HcRWKi8', 'name': 'pMODU6-pGALZ4-P1G1-HygMX'},
                        {'id': 'seq_IyZI9bEh', 'name': 'pMODU6-pGAL1-FAR1-L1-IAA17T1_opt'},
                        {'id': 'seq_iGdjEEx4', 'name': 'pGPT4-pGAL1-P1G1-GEV'}, {'id': 'seq_AgQ1w9ak', 'name': 'pLAB2'},
                        {'id': 'seq_QuWMpfRK', 'name': 'pMODT4-pGAL1-attB1-GVNY'},
                        {'id': 'seq_etTsAfD4', 'name': 'pGPU6-pGALZ4-eYFP'},
                        {'id': 'seq_5AXMlSvB', 'name': 'pYMOD2Kmx_pGAL1-HYG_pGAL1-iaah'},
                        {'id': 'seq_K5hwGNwg', 'name': 'pMODU6-pGAL1-BleoMX'},
                        {'id': 'seq_Na2oNxzs', 'name': 'pMODU6-pGALZ4-FAR1-mut-87aa'},
                        {'id': 'seq_2rKmILGU', 'name': 'pMODU6-pGAL1-NatMX'},
                        {'id': 'seq_qihkmlW4', 'name': 'pMODU6-pGAL1-AlphaFactor'},
                        {'id': 'seq_rwDoRd9Q', 'name': 'pMODU6-pGALZ4-FAR1'},
                        {'id': 'seq_QGfqobtP', 'name': 'pGPT4-pGAL1-AVNY'},
                        {'id': 'seq_hhI5TTbO', 'name': 'pMODU6-pGAL1-FAR1-IAA17T2'},
                        {'id': 'seq_tMz0Xv3g', 'name': 'pMODU6-pGAL1-FAR1-L1-IAA17T2'},
                        {'id': 'seq_PKJNfuZA', 'name': 'pGPH8-pGAL1-GAVNY_v2'},
                        {'id': 'seq_4ccBmI1j', 'name': 'pGPU6-pGAL1-AFB2'},
                        {'id': 'seq_Qc6f2Kii', 'name': 'pMOD4G-NLS_dCas9_VP64'},
                        {'id': 'seq_k0MuYdIM', 'name': 'pMODU6-pGAL1-IAA17T2-FAR1'},
                        {'id': 'seq_F4tEc0XU', 'name': 'pMODU6-pGALZ4-STE5(-)RING'},
                        {'id': 'seq_2xGw2yCj', 'name': 'pGPH8-pGAL1-GAVNY'},
                        {'id': 'seq_9ph0SnJV', 'name': 'AmpR-T4-pGAL1-GAL4DBD-L1'},
                        {'id': 'seq_D1iAdKMz', 'name': 'pGPL5G-pGAL1-URA3'},
                        {'id': 'seq_wHiaXdFM', 'name': 'pGPT4-pGAL1-G(m)AVNY'},
                        {'id': 'seq_VazadBJw', 'name': 'pGPT4-pGAL1-GAVNY'},
                        {'id': 'seq_w2IZPFzd', 'name': 'pMODOK-pACT1-GAVNY'},
                        {'id': 'seq_fkFjzKkb', 'name': 'v63_pGP8zGAL-STE5(-)RING-SNC2 C-term'},
                        {'id': 'seq_i0Yl6uzk', 'name': 'pMODH8-pGPD-TIR1_DM'},
                        {'id': 'seq_m42PVReQ', 'name': 'pMODT4-pGALZ4-Z4AVNY'},
                        {'id': 'seq_WQ0wqb9f', 'name': 'pMODU6-pGALZ4-iaaH'},
                        {'id': 'seq_l5VHTc8Z', 'name': 'pGPU6-pGAL1-TIR1_DM'},
                        {'id': 'seq_kKtPZ1Rs', 'name': 'pMODT4-pGAL1-P1G1-GAVNY'},
                        {'id': 'seq_usn0K27s', 'name': 'pMODU6-pGALZ4-BleoMX'},
                        {'id': 'seq_rzQGBzv2', 'name': 'pGP5G-ccdB'},
                        {'id': 'seq_bw3XWuZU', 'name': 'pMODT4-pGALZ4-AVNY'},
                        {'id': 'seq_SGfG2YeB', 'name': 'pMODU6-pGALZ4-HygMX'},
                        {'id': 'seq_TWAJLtvz', 'name': 'pMODU6-pGAL1-P1G1-HygMX'},
                        {'id': 'seq_tFGIIL0C', 'name': 'pMODU6-pGAL1-FAR1'},
                        {'id': 'seq_6VN5FDpP', 'name': 'pMODOK-pACT1-GAVN'},
                        {'id': 'seq_y9xdtVx7', 'name': 'pMODKan-HO-pACT1GEV'},
                        {'id': 'seq_AyQ7ToIn', 'name': 'pBR322 (Sample Sequence)'},
                        {'id': 'seq_GuqSGBXY', 'name': 'pGPT4-pGAL1-GAVNY(VP64) new design'},
                        {'id': 'seq_UbsucV1t', 'name': 'pMODU6-pGAL1-HygMX'},
                        {'id': 'seq_TsTM0B8q', 'name': 'pMOD4-pGAL1Z3(P3)-MF(AL'}], 'type': 'ALL'}

schema = SequenceSchema()
data = schema.load(seq)
pprint(data.errors)
pprint(data.data)

seq = data.data
schema.dump(seq)

schema = FolderSchema()
data = schema.load(folder)
pprint(data.errors)
pprint(data.data)
