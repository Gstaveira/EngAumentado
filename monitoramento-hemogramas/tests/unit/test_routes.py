import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hemograma" in response.data

def test_upload_page(client):
    response = client.get("/upload")
    assert response.status_code == 200

def test_api_predict_route(client):
    response = client.post("/predict", json={"hemacias": 4.5})
    assert response.status_code in [200, 400]
