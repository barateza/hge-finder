from app import create_app


def test_index_returns_200_and_message():
    app = create_app()
    client = app.test_client()

    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["message"] == "Hello, World!"
