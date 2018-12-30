import os
import re
import sys
from distutils.core import setup
from setuptools.command.install import install


tests_require = [
    'pytest',
    'pytest-cov',
    'vcrpy'
]

# 3.0.0b12
install_requires = [
    "requests",
    "marshmallow==3.0.0rc1",
    "inflection",
]

def parse_version_file():
    here = os.path.abspath(os.path.dirname(__file__))
    ver_dict = {}
    with open(os.path.join(here, 'benchlingapi', '__version__.py'), 'r') as f:
        for line in f.readlines():
            m = re.match('__(\w+)__\s*=\s*(.+)', line)
            if m:
                key = m.group(1)
                val = m.group(2)
                val = re.sub("[\'\"]", "", val)
                ver_dict[key] = val
    return ver_dict


def readme():
    """print long description"""
    with open('README.rst') as f:
        return f.read()


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != ver['version']:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, ver['version']
            )
            sys.exit(info)


ver = parse_version_file()

# setup
setup(
        title=ver['title'],
        name='benchlingapi',
        version=ver['version'],
        packages=["benchlingapi", 'benchlingapi.models'],
        long_description=readme(),
        url=ver['url'],
        license='',
        author=ver['author'],
        author_email=ver['author_email'],
        keywords='',
        description=ver['description'],
        install_requires=install_requires,
        python_requires='>=3.4',
        tests_require=tests_require,
        classifiers=[],
        cmdclass={
            'verify': VerifyVersionCommand,
        }
)