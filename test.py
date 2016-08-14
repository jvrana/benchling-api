# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 07:48:14 2015

@author: Justin
"""
from benchlingapi import BenchlingAPI, BenchlingAPIException

from nose.tools import assert_equal, assert_true, assert_raises

bench_api_key = 'sk_GbNYfhnukDU30J5fAebIjEj0d4YlJ'


def testBenchlingAPIConstruction():
    global api
    api = BenchlingAPI('sk_GbNYfhnukDU30J5fAebIjEj0d4YlJ')
    print 'Logged in'

    sequences = api._get('sequences', data={'limit': 10})
    print len(sequences['sequences'])
testBenchlingAPIConstruction()