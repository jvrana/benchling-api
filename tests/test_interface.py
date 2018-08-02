import pytest
from benchlingapi.models import __all__
from benchlingapi.exceptions import ModelNotFoundError

def test_all_models(session):

    assert len(session.models) == len(__all__)


def test_model_interface(session):

    for model_name in __all__:
        interface = session.interface(model_name)
        interface_from_attr = getattr(session, model_name)

        print(interface)

        assert type(interface) is type(interface_from_attr)
        assert interface is not None


def test_raise_no_model(session):

    with pytest.raises(ModelNotFoundError):
        session.interface("ModelDoesntExist")
