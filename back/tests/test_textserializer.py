from api.views import TextSerializer


def test_serialize():
    obj = {
        'foo': [1, 2, 3],
        'bar': {
            'foo': 'bar',
            'bar': 'foo',
            'baz': 'quux',
        }
    }
    text = TextSerializer().serialize(obj)
    lines = text.split('\n')
    assert len(lines) == 6, 'Incorrect number of lines'
    assert lines[0] == 'foo.0=1'
    assert lines[1] == 'foo.1=2'
    assert lines[2] == 'foo.2=3'
    assert lines[3] == 'bar.foo="bar"'
    assert lines[4] == 'bar.bar="foo"'
    assert lines[5] == 'bar.baz="quux"'

def test_deserialize():
    text = """
        foo.0=1
        foo.1.bar=1
    """
    obj = TextSerializer().deserialize(text)
    assert obj['foo'][0] == 1
    assert obj['foo'][1]['bar'] == 1
