from typing import Any

import requests

from app.config import settings


class HCPClient:
    """
    HTTP client used by the Telegram client to communicate with an HCP Node.

    This class is intentionally lightweight and only exposes protocol
    operations defined by HCP.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.base_url = (base_url or settings.hcp_node_url).rstrip("/")
        self.timeout = timeout or settings.request_timeout

    def health(self) -> dict[str, Any]:
        """
        Check whether the configured HCP Node is reachable.
        """
        response = requests.get(
            f"{self.base_url}/health",
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def create_record(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Submit one canonical Humanitarian Record to the HCP Node.
        """
        response = requests.post(
            f"{self.base_url}/hcp/records",
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def search_records(
        self,
        query: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Submit a Humanitarian Query to the HCP Node.

        The HCP Reference Node expects POST /hcp/search using the canonical
        HumanitarianQuery JSON structure.
        """
        response = requests.post(
            f"{self.base_url}/hcp/search",
            json=query,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def get_record(
        self,
        record_id: str,
    ) -> dict[str, Any]:
        """
        Retrieve one Humanitarian Record by its identifier.
        """
        response = requests.get(
            f"{self.base_url}/hcp/records/{record_id}",
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()
