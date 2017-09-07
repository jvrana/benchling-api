from benchlingapi import *
import pytest
import json

@pytest.fixture
def get_config():
    config_location = "tests/secrets/config.json"
    with open(config_location, 'rU') as handle:
        return json.load(handle)

@pytest.fixture
def api_init():
    return BenchlingAPI(**get_config()["credentials"])

def test_main():
    api = api_init()

    print(api.folders)

    # https: // docs.pytest.org / en / latest / builtin.html
    # def test1():
    #     with pytest.raises(ValueError) as e:
    #         dosomething()
    #     pytest.approx
    #     