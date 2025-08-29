import pytest
from fastapi.testclient import TestClient
from taman.main import app

client = TestClient(app)


def test_get_processes():
    """Test the /process endpoint."""
    response = client.get("/process")
    assert response.status_code == 200
    
    data = response.json()
    assert "processes" in data
    assert isinstance(data["processes"], list)


def test_app_info():
    """Test that the app has correct metadata."""
    assert app.title == "Taman System Monitor API"
    assert app.version == "0.1.0"


def test_kill_process_invalid_pid():
    """Test killing a process with invalid PID."""
    response = client.get("/kill/999999")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    # Should be either success or error depending on system


def test_stream_endpoint():
    """Test that the stream endpoint is accessible."""
    response = client.get("/process/stream")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"