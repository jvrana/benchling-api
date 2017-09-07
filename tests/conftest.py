import pytest
from benchlingapi import BenchlingAPI
import os
import json

@pytest.fixture
def config(scope="module"):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    config_location = os.path.join(test_dir, "secrets/config.json")
    with open(config_location, 'rU') as handle:
        return json.load(handle)

@pytest.fixture(scope="module")
def api():
    return BenchlingAPI(**config()["credentials"])