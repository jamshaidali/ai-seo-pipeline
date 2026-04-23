import pytest
from app import create_app
from app.extensions import db
from app.models.profile import BusinessProfile
import json

@pytest.fixture
def client():
    app = create_app('config.TestingConfig')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_create_profile(client):
    data = {
        "name": "Test Business",
        "domain": "test.com",
        "industry": "Technology",
        "description": "A test business",
        "competitors": ["competitor1.com", "competitor2.com"]
    }
    response = client.post('/api/v1/profiles', 
                          data=json.dumps(data), 
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'profile_uuid' in data
    assert data['name'] == 'Test Business'

def test_get_profile_not_found(client):
    response = client.get('/api/v1/profiles/12345678-1234-5678-9012-123456789012')
    assert response.status_code == 404

def test_create_profile_validation_error(client):
    data = {"name": ""}  # Invalid
    response = client.post('/api/v1/profiles', 
                          data=json.dumps(data), 
                          content_type='application/json')
    assert response.status_code == 400

def test_rate_limiting_create_profile(client):
    data = {
        "name": "Test Business",
        "domain": "test.com",
        "industry": "Technology",
        "description": "A test business",
        "competitors": ["competitor1.com"]
    }
    # This test would need to be adjusted for actual rate limiting testing
    # For now, just ensure endpoint works
    response = client.post('/api/v1/profiles', 
                          data=json.dumps(data), 
                          content_type='application/json')
    assert response.status_code in [201, 429]  # 429 if rate limited