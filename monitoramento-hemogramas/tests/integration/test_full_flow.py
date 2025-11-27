from app import app
import pytest
import io

@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()

def test_fluxo_completo(client):
    csv_data = b"hemacias,leucocitos,plaquetas\n4.5,7000,250000"
    rv = client.post(
        "/upload",
        data={"file": (io.BytesIO(csv_data), "teste.csv")},
        content_type="multipart/form-data",
    )
    assert rv.status_code == 200
