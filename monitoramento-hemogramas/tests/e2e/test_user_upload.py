def test_user_upload_flow(client):
    rv = client.get("/")
    assert rv.status_code == 200
