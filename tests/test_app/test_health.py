"""Tests for app/ package — health endpoint and API basics."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    """Create a test client."""
    app = create_app()
    return TestClient(app)


def test_health_endpoint(client):
    """GET /health returns 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "mock_mode" in data
    assert "version" in data


def test_health_no_auth_required(client):
    """Health endpoint should not require authentication."""
    response = client.get("/health")
    assert response.status_code == 200


def test_api_requires_auth(client):
    """API endpoints should require Bearer token."""
    response = client.get("/api/v1/apix/daily")
    assert response.status_code in (401, 403)  # No auth header


def test_api_with_valid_token(client):
    """API endpoints should work with valid token."""
    response = client.get(
        "/api/v1/apix/daily",
        headers={"Authorization": "Bearer change-me-dev-token"},
    )
    assert response.status_code == 200
