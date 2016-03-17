bench_api_key = 'sk_g7fo2vxkNUYNPkShOFIOmtY9ejIGE'
aq_api_key = 'ZeMgEm1B9Hy7kt1KdUVFZlYV3bT7R7hSGE4YavrlVlc'
aq_user = 'vrana'
aq_url = 'http://54.68.9.194:81/api'
import requests
from benchlingapi import *
credentials = [bench_api_key,
                       aq_url,
                       aq_user,
                       aq_api_key]
portal = BenchlingPortal(*credentials)

print portal.folder_dict