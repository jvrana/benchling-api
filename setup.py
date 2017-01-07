try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
	from distutils.command.build_py import build_py_2to3 \
		as build_py
except ImportError:
	from distutils.command.build_py import build_py

config = {
    'description': 'benchling-api',
    'author': 'Justin Vrana',
    'url': 'https://github.com/klavinslab/benchling-api',
    'download_url': 'https://github.com/klavinslab/benchling-api.git',
    'author_email': 'justin.vrana@gmail.com',
    'version': '0.9.0',
    'install_requires': ['requests', 'bs4'], #, 'aquariumapi'],
    #'extras_require': {'benclingportal': ['coral', 'aquariumapi'],
    'packages': ['benchlingapi'],
    'tests_require': ['pytest'],
    'scripts': [],
    'name': 'benchlingapi',
    'license': 'Copyright University of Washington'
}

setup(**config)
