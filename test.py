# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 07:48:14 2015

@author: Justin
"""
from benchlingapi import BenchlingAPI, BenchlingAPIException

from nose.tools import assert_equal, assert_true, assert_raises

bench_api_key = 'sk_GbNYfhnukDU30J5fAebIjEj0d4YlJ'

api = None

def testBenchlingAPIConstruction():
    bench_api_key = 'sk_g7fo2vxkNUYNPkShOFIOmtY9ejIGE'
    global api
    api = BenchlingAPI(bench_api_key)

def testCreateFolder():
