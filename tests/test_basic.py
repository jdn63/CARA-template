# tests/test_basic.py

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'CARA' in response.data