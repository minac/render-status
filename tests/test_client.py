"""Tests for Render API client."""

import pytest
import httpx
from unittest.mock import Mock, patch

from render_status_deploys.client import RenderClient


class TestRenderClient:
    """Test Render API client."""

    def test_client_initialization(self):
        """Test client is initialized with correct headers."""
        client = RenderClient("test-key")
        assert client.api_key == "test-key"
        assert client.client.headers["Authorization"] == "Bearer test-key"
        assert client.client.headers["Accept"] == "application/json"
        client.client.close()

    def test_context_manager(self):
        """Test client works as context manager."""
        with RenderClient("test-key") as client:
            assert client.api_key == "test-key"

    @patch("httpx.Client.get")
    def test_get_services_success(self, mock_get):
        """Test fetching services successfully."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"service": {"id": "srv-1", "name": "service-1", "type": "web_service"}},
            {"service": {"id": "srv-2", "name": "service-2", "type": "cron_job"}},
        ]
        mock_get.return_value = mock_response

        with RenderClient("test-key") as client:
            services = client.get_services()

        assert len(services) == 2
        assert services[0]["id"] == "srv-1"
        mock_get.assert_called_once_with("/services")
        mock_response.raise_for_status.assert_called_once()

    @patch("httpx.Client.get")
    def test_get_services_failure(self, mock_get):
        """Test fetching services with HTTP error."""
        mock_get.side_effect = httpx.HTTPError("API error")

        with RenderClient("test-key") as client:
            with pytest.raises(httpx.HTTPError):
                client.get_services()

    @patch("httpx.Client.get")
    def test_get_deploys_success(self, mock_get):
        """Test fetching deploys successfully."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"deploy": {"id": "dep-1", "status": "live", "createdAt": "2025-11-25T12:00:00Z"}},
        ]
        mock_get.return_value = mock_response

        with RenderClient("test-key") as client:
            deploys = client.get_deploys("srv-1", limit=5)

        assert len(deploys) == 1
        assert deploys[0]["status"] == "live"
        mock_get.assert_called_once_with("/services/srv-1/deploys", params={"limit": 5})
        mock_response.raise_for_status.assert_called_once()

    @patch("httpx.Client.get")
    def test_get_jobs_success(self, mock_get):
        """Test fetching jobs successfully."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "job-1", "status": "succeeded", "createdAt": "2025-11-25T13:00:00Z"},
        ]
        mock_get.return_value = mock_response

        with RenderClient("test-key") as client:
            jobs = client.get_jobs("srv-2")

        assert len(jobs) == 1
        assert jobs[0]["status"] == "succeeded"
        mock_get.assert_called_once_with("/services/srv-2/jobs")
        mock_response.raise_for_status.assert_called_once()
