import toml
from os.path import dirname, abspath, join
import json
from os import getenv
from os.path import isfile
import sys

here = dirname(abspath(__file__))
INPATH = join(here, "../../pyproject.toml")
OUTPATH = join(here, "version.json")


def pull_version():
    """Pulls version from pyproject.toml and moves to version JSON"""
    config = toml.load(INPATH)
    ver_data = dict(config["tool"]["poetry"])
    try:
        with open(OUTPATH, "r") as f:
            print(">> Previous Version:")
            print(f.read())
    except:
        pass

    with open(OUTPATH, "w") as f:
        print("<< New Version (path={}):".format(OUTPATH))
        print(json.dumps(ver_data, indent=2))
        json.dump(ver_data, f, indent=2)


def parse_version():
    """Parses version JSON"""
    if isfile(OUTPATH):
        with open(OUTPATH, "r") as f:
            ver = json.load(f)
        return ver
    else:
        return {}


if __name__ == "__main__":
    pull_version()


ver = parse_version()


def get_version():
    v = ver.get("version", None)
    print(v)
    return v


def get_name():
    name = ver.get("name", None)
    print(name)
    return name


def verify_ci():
    tag = getenv("CIRCLE_TAG")

    if tag != ver.get("version", None):
        info = "Git tag: {0} does not match the version of this app: {1}".format(
            tag, ver.get("version", None)
        )
        sys.exit(info)


__version__ = ver.get("version", None)
__title__ = ver.get("name")
__author__ = ver.get("authors")
__homepage__ = ver.get("homepage")
__repo__ = ver.get("repository")
