try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'benchling-api',
    'author': 'Justin D Vrana',
    'url': 'https://github.com/klavinslab/benchling-api',
    'download_url': 'https://github.com/klavinslab/benchling-api.git',
    'author_email': 'justin.vrana@gmail.com',
    'version': '0.9.1',
    'install_requires': ['requests', 'bs4'],
    'packages': ['benchlingapi'],
    'tests_require': ['pytest'],
    'scripts': [],
    'name': 'benchlingapi',
    'license': 'Copyright University of Washington'
}

setup(**config)
