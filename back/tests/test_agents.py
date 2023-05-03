from api.models import Agent

def test_agent_create(client):
    "Ensure we can create if not authenticated."
    r = client.post('/api/agents/', json={
        'uuid': '22a92175-d3aa-4d11-9a75-f19de56ef030',
        'name': 'Test Agent',
        'token': 'abc123',
    })
    assert r.status_code == 201, 'Created'
    a = Agent.get(Agent.id == r.json['id'])
    assert a.activated == False

def test_agent_auth(agent):
    r = agent.get('/api/agents/1/')
    assert r.status_code == 200, 'OK'
    assert r.json.get('activated') is True

def test_hosts_port_scan(authenticated):
    "Ensure we can activate if authenticated."
    a = Agent.create(uuid='22a92175-d3aa-4d11-9a75-f19de56ef030', name='Test Agent', token='abc123')
    r = authenticated.put('/api/agents/1/', json={
        'activated': True,
    })
    assert r.status_code == 202, 'Accepted'
    assert r.json.get('activated') is True
