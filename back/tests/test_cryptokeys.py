from unittest.mock import MagicMock

from api.models import Frontend, Backend


SSH_KEY = 'AAAAB3NzaC1yc2EAAAADAQABAAABgQDAO3IDQeSwgMe+5FNFjq0YnmUiLoHn+BlX1L3k0lgyZe2vDwOwN6ZTDZXjDOpezDYID4r8K/yOL/4Xn4lYSD27b2p+vDvyqA+BgRq8xc+OuyDEwfm20AS0WG9F9+Yagj8v9cd5kS9vkkPFPZ+5F6nzFA04CDnWfpcTdoMVCMEc+Q5KG2VwBeFIaWegeg1bxqbJq3J37dpm+t8EEgyJDxnkSIXLMzKs7yoqrpjOSedppzGYwa+OnS4GWDsHomwvpkP//QGYKlPEpS/6Y5cNdLL86sRdOtT2nvwRKw/3W3P1dVp2rcqiwVzc/9C3wO+u8M2vgBYZMbyPsoOjSs1o5r4tCAi56d+EdDPK/aFCDOQoRk4007eAr0vdQ6L7FVGosuxJ7LzSCqw7rY6ArWD2BVuUalwFC1KEIJiGOfEHYQM+Awfnul7ZD29nLxUhSw37zqadnBUjyFIkzvvPfmxJoiLy7jjVDIi4p1yRbL0j/DFyPdtcIszosbDdS8i7xx4BMQs='


def test_cryptokeys_issue(authenticated):
    "Ensure we can issue SSL certs."
    backend = Backend.create(
        name='Test Backend',
        url='http://foo:8000/',
        container_id='adfsfadf870sfs09f8s0fd9',
    )
    frontend = Frontend.create(
        type='tunnel',
        backend=backend,
        url='http://domain.tld/',
    )
    r = authenticated.post('/api/cryptokeys/issue/', json={
        'frontend_id': frontend.id,
    })
    assert r.status_code == 200, f'Invalid status {r.status_code}'

def test_cryptokeys_sshkey(authenticated, mocker):
    mocker.patch(
        'api.app.oauth.shanty.get', return_value=MagicMock(
            status_code=200,
            json=MagicMock(return_value=[
                { 'type': 'ssh-rsa', 'key': SSH_KEY }
            ])
        ))
    mocker.patch('api.app.oauth.shanty.post', return_value=MagicMock(status_code=201))
    r = authenticated.post('/api/cryptokeys/sshkey/', json={
        'type': 'ssh-rsa',
        'public': SSH_KEY,
    })
    assert r.status_code == 200, f'Invalid status {r.status_code}'
