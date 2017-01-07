from benchlingapi.benchlingapi import BenchlingAPI
from glob import glob
import os
import json


def test_alignments():
    login_location = os.path.join(os.path.dirname(__file__), '../data/login.json')
    with open(login_location, 'r') as f:
        credentials = json.load(f)

    api = BenchlingAPI(credentials['benchling_api_key'])

    r = api.submit_mafft_alignment('seq_P2RlpQNY', queries=glob('test_data/*ab1'))
    taskid = r['statusUrl'].split('/')[-1]
    print api.get_task(taskid)