

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
        c = cor.DNA(bs['bases'],
        bottom=None,
        circular=bs['circular'],
        name=bs['name'])
        for a in bs['annotations']:
            name = a['name'].encode('utf-8').strip()
            start = a['start']
            stop = a['end']
            strand = 0 if a['strand'] == 1 else 1
            qualifiers = {
                'label': name,
                'ApEinfo_fwdcolor': [a['color']],
                'ApEinfo_revcolor': [a['color']]}
            ftype = a['type'].encode('utf-8').strip()
            if ftype not in list(set(cor.constants.genbank.TO_CORAL)):
                ftype = 'misc_feature'
            f = cor.Feature(name, start, stop, ftype, strand=strand, qualifiers=qualifiers)
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