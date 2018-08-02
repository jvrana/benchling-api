import json
import os

import pytest

from benchlingapi.session import Session


@pytest.fixture
def config(scope="module"):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    config_location = os.path.join(test_dir, "secrets/config.json")
    with open(config_location, 'rU') as handle:
        return json.load(handle)


@pytest.fixture(scope="module")
def session():
    return Session(config()["credentials"]["api_key"])
