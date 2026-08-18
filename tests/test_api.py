import os
import sys
from datetime import datetime, timedelta
from urllib.parse import urlparse

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402
import models  # noqa: E402

TEST_DB_URL = "sqlite:///./test_vulntracker.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def register_and_login(username="alice", email="alice@example.com", password="password123"):
    client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    resp = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_scan(token, title="Test finding", severity="low"):
    resp = client.post(
        "/scans",
        json={
            "title": title,
            "severity": severity,
            "affected_component": "misc",
        },
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# Baseline tests
# ---------------------------------------------------------------------------

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_register_user():
    resp = client.post(
        "/auth/register",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "secret",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["username"] == "bob"


def test_register_duplicate_username():
    payload = {"username": "bob", "email": "bob@example.com", "password": "secret"}
    client.post("/auth/register", json=payload)
    resp = client.post(
        "/auth/register",
        json={**payload, "email": "bob2@example.com"},
    )
    assert resp.status_code == 400


def test_login_success():
    client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "pw"},
    )
    resp = client.post(
        "/auth/login",
        json={"username": "alice", "password": "pw"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password():
    client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "pw"},
    )
    resp = client.post(
        "/auth/login",
        json={"username": "alice", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_create_scan():
    token = register_and_login()
    resp = client.post(
        "/scans",
        json={
            "title": "Reflected XSS in search",
            "description": "User input is echoed without sanitisation",
            "severity": "high",
            "affected_component": "GET /search",
        },
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Reflected XSS in search"


def test_list_scans():
    token = register_and_login()
    create_scan(token)
    resp = client.get("/scans", headers=auth_headers(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_search_scans():
    token = register_and_login()
    create_scan(token, title="SQL Injection via login", severity="critical")
    resp = client.get("/scans/search?q=SQL", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    assert resp.json()["results"][0]["title"] == "SQL Injection via login"


def test_update_scan_status():
    token = register_and_login()
    scan_id = create_scan(token, title="Open redirect", severity="medium")["id"]
    resp = client.patch(
        f"/scans/{scan_id}",
        json={"status": "in_progress"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


def test_delete_scan():
    token = register_and_login()
    scan_id = create_scan(token, title="Stale finding")["id"]
    resp = client.delete(
        f"/scans/{scan_id}",
        headers=auth_headers(token),
    )
    assert resp.status_code == 204


# ---------------------------------------------------------------------------
# Authorization/security regression tests
# ---------------------------------------------------------------------------

def test_get_scan_is_owner_scoped():
    alice = register_and_login("alice", "alice@example.com")
    bob = register_and_login("bob", "bob@example.com")
    scan_id = create_scan(alice, title="Alice confidential finding")["id"]

    resp = client.get(
        f"/scans/{scan_id}",
        headers=auth_headers(bob),
    )
    assert resp.status_code == 404


def test_search_is_owner_scoped():
    alice = register_and_login("alice", "alice@example.com")
    bob = register_and_login("bob", "bob@example.com")
    create_scan(alice, title="Alice confidential finding")

    resp = client.get(
        "/scans/search?q=confidential",
        headers=auth_headers(bob),
    )
    assert resp.status_code == 200
    assert resp.json()["count"] == 0



def test_unsigned_jwt_is_rejected():
    import base64
    import json

    def b64(value):
        return base64.urlsafe_b64encode(value).rstrip(b"=").decode()

    header = b64(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    payload = b64(json.dumps({"sub": "alice"}).encode())
    unsigned = f"{header}.{payload}."

    resp = client.get(
        "/scans",
        headers={"Authorization": f"Bearer {unsigned}"},
    )
    assert resp.status_code == 401

# ---------------------------------------------------------------------------
# Shared report link tests
# ---------------------------------------------------------------------------

def test_create_share_link():
    token = register_and_login()
    scan_id = create_scan(token, title="Shareable finding")["id"]

    resp = client.post(
        f"/scans/{scan_id}/share",
        json={},
        headers=auth_headers(token),
    )

    assert resp.status_code == 200
    share_url = resp.json()["share_url"]
    assert "/share/" in share_url
    assert len(urlparse(share_url).path.rsplit("/", 1)[-1]) >= 40


def test_public_share_link_returns_reduced_scan():
    token = register_and_login()
    scan = create_scan(token, title="Public report")
    share_resp = client.post(
        f"/scans/{scan['id']}/share",
        json={},
        headers=auth_headers(token),
    )
    share_url = share_resp.json()["share_url"]

    resp = client.get(urlparse(share_url).path)

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == scan["id"]
    assert body["title"] == "Public report"
    assert "owner_id" not in body
    assert resp.headers["cache-control"] == "no-store"
    assert resp.headers["referrer-policy"] == "no-referrer"


def test_password_protected_share_link():
    token = register_and_login()
    scan = create_scan(token, title="Password protected")
    share_resp = client.post(
        f"/scans/{scan['id']}/share",
        json={"password": "correct-horse-battery"},
        headers=auth_headers(token),
    )
    share_url = share_resp.json()["share_url"]
    path = urlparse(share_url).path

    missing = client.get(path)
    wrong = client.get(path, params={"password": "wrong-password"})
    correct = client.get(path, params={"password": "correct-horse-battery"})

    assert missing.status_code == 401
    assert wrong.status_code == 401
    assert correct.status_code == 200
    assert correct.json()["title"] == "Password protected"


def test_share_link_expires_after_24_hours():
    token = register_and_login()
    scan = create_scan(token, title="Expiring report")
    share_resp = client.post(
        f"/scans/{scan['id']}/share",
        json={},
        headers=auth_headers(token),
    )
    share_url = share_resp.json()["share_url"]
    share_token = urlparse(share_url).path.rsplit("/", 1)[-1]

    db = TestingSessionLocal()
    try:
        share = (
            db.query(models.ShareToken)
            .filter(models.ShareToken.token_hash.isnot(None))
            .first()
        )
        assert share is not None
        share.expires_at = datetime.utcnow() - timedelta(minutes=1)
        db.commit()
    finally:
        db.close()

    resp = client.get(f"/share/{share_token}")
    assert resp.status_code == 404


def test_invalid_share_token():
    resp = client.get("/share/this-token-does-not-exist")
    assert resp.status_code == 404


def test_only_scan_owner_can_create_share_link():
    alice = register_and_login("alice", "alice@example.com")
    bob = register_and_login("bob", "bob@example.com")
    scan_id = create_scan(alice, title="Alice-only finding")["id"]

    resp = client.post(
        f"/scans/{scan_id}/share",
        json={},
        headers=auth_headers(bob),
    )
    assert resp.status_code == 404
