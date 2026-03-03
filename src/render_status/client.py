"""Render API client."""

from typing import Any

import httpx
import structlog

log = structlog.get_logger()


class RenderClient:
    """Client for Render API."""

    BASE_URL = "https://api.render.com/v1"
    TIMEOUT = 30.0

    def __init__(self, api_key: str):
        """Initialize Render client.

        Args:
            api_key: Render API key
        """
        self.api_key = api_key
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            },
            timeout=self.TIMEOUT,
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.client.close()

    def get_services(self) -> list[dict[str, Any]]:
        """Fetch all services.

        Returns:
            List of service objects

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        try:
            response = self.client.get("/services")
            response.raise_for_status()
            data = response.json()
            # Extract service objects from wrapper
            services = [item["service"] for item in data]
            log.info("fetched services", count=len(services))
            return services
        except httpx.HTTPError as e:
            log.error("failed to fetch services", error=str(e))
            raise

    def get_deploys(self, service_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Fetch deploys for a service.

        Args:
            service_id: Service ID
            limit: Maximum deploys to fetch

        Returns:
            List of deploy objects

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        try:
            response = self.client.get(f"/services/{service_id}/deploys", params={"limit": limit})
            response.raise_for_status()
            data = response.json()
            # Extract deploy objects from wrapper
            deploys = [item["deploy"] for item in data]
            log.info("fetched deploys", service_id=service_id, count=len(deploys))
            return deploys
        except httpx.HTTPError as e:
            log.error("failed to fetch deploys", service_id=service_id, error=str(e))
            raise

    def get_jobs(self, service_id: str) -> list[dict[str, Any]]:
        """Fetch cron jobs for a service.

        Args:
            service_id: Service ID

        Returns:
            List of job objects

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        try:
            response = self.client.get(f"/services/{service_id}/jobs")
            response.raise_for_status()
            data = response.json()
            # Extract job objects from wrapper if present
            jobs = (
                [item["job"] for item in data]
                if data and isinstance(data[0], dict) and "job" in data[0]
                else data
            )
            log.info("fetched jobs", service_id=service_id, count=len(jobs))
            return jobs
        except httpx.HTTPError as e:
            log.error("failed to fetch jobs", service_id=service_id, error=str(e))
            raise
