def test_create_settings_text(client):
    "Ensure we can create settings using text format."
    r = client.post('/api/settings/?format=text', data='FOO=foo')
    r = client.post('/api/settings/?format=text', data='bar=BAR')
    assert r.get_data() == b'BAR=BAR', 'Name not uppercase'
