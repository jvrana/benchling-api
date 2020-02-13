from benchlingapi import Session


def test_session(session):
    pass


def test_setting_org():
    session = Session('alsdfja;lsdfj', org='myorganization')
    assert session.url == 'https://myorganization.benchling.com/api/v2'


def test_setting_home():
    home = 'https://myotherorganization.benchling.com/api/v2'
    session = Session('alsdfja;lsdfj', home=home)
    assert session.url == home