# tests/test_api.py

def test_homepage_loads(client):
    """Test that the homepage loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Wisconsin' in response.data or b'CARA' in response.data

def test_app_configuration(client):
    """Test that the Flask app is properly configured for testing"""
    # Test that the app exists and has testing configuration
    with client.application.app_context():
        assert client.application.config['TESTING'] is True
        assert 'sqlite' in client.application.config['SQLALCHEMY_DATABASE_URI']