from fastapi.testclient import TestClient


def test_guest_can_search_routes(client: TestClient) -> None:
    response = client.get("/routes", headers={"X-Role": "guest"})
    assert response.status_code == 200


def test_guest_cannot_upload_feed(client: TestClient) -> None:
    response = client.post(
        "/feeds",
        headers={"X-Role": "guest"},
        files={"file": ("feed.zip", b"", "application/zip")},
    )
    assert response.status_code == 403


def test_guest_cannot_subscribe(client: TestClient) -> None:
    response = client.post(
        "/subscriptions",
        headers={"X-Role": "guest"},
        json={"user_id": 1, "route_id": 1},
    )
    assert response.status_code == 403


def test_user_cannot_upload_feed(client: TestClient) -> None:
    response = client.post(
        "/feeds",
        headers={"X-Role": "user"},
        files={"file": ("feed.zip", b"", "application/zip")},
    )
    assert response.status_code == 403


def test_admin_can_upload_feed(client: TestClient) -> None:
    response = client.post(
        "/feeds",
        headers={"X-Role": "admin"},
        files={"file": ("feed.zip", b"", "application/zip")},
    )
    # 422, бо файл невалідний, але роль дозволена
    assert response.status_code == 422


def test_invalid_role_returns_400(client: TestClient) -> None:
    response = client.post(
        "/feeds",
        headers={"X-Role": "superadmin"},
        files={"file": ("feed.zip", b"", "application/zip")},
    )
    assert response.status_code == 400
