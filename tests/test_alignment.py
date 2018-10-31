def test_alignment(session):
    session.http.HOME = 'https://benchling.com/api/v2'
    session.http.post("multi-align")