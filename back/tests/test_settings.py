def test_settings_auth(client):
    "Ensure we cannot create settings when not logged in."
    r = client.post('/api/settings/?format=text', data='FOO=foo')
    assert r.status_code == 401, 'Invalid status code'

def test_create_settings_text(authenticated):
    "Ensure we can create settings using text format."
    r = authenticated.post('/api/settings/?format=text', data='FOO=foo')
    assert r.status_code == 201, 'Invalid status code'
    r = authenticated.post('/api/settings/?format=text', data='bar=BAR')
    assert r.status_code == 201, 'Invalid status code'
    assert r.get_data() == b'BAR=BAR', 'Name not uppercase'
