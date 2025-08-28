import os
from typing import Any

import httpx
from loguru import logger

from universal_mcp.exceptions import NotAuthorizedError


class AgentrClient:
    """Helper class for AgentR API operations.

    This class provides utility methods for interacting with the AgentR API,
    including authentication, authorization, and credential management.

    Args:
        api_key (str, optional): AgentR API key. If not provided, will look for AGENTR_API_KEY env var.
        base_url (str, optional): Base URL for AgentR API. Defaults to https://api.agentr.dev.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        base_url = base_url or os.getenv("AGENTR_BASE_URL", "https://api.agentr.dev")
        self.base_url = f"{base_url.rstrip('/')}/v1"
        self.api_key = api_key or os.getenv("AGENTR_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided and AGENTR_API_KEY not found in environment variables")
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"X-API-KEY": self.api_key},
            timeout=30,
            follow_redirects=True,
            verify=False,
        )

    def get_credentials(self, app_id: str) -> dict[str, Any]:
        """Get credentials for an integration from the AgentR API.

        Args:
            app_id (str): The ID of the app (e.g., 'asana', 'google-drive').

        Returns:
            dict: Credentials data from API response.

        Raises:
            NotAuthorizedError: If credentials are not found (404 response).
            HTTPError: For other API errors.
        """
        response = self.client.get(
            "/credentials/",
            params={"app_id": app_id},
        )
        if response.status_code == 404:
            logger.warning(f"No credentials found for app '{app_id}'. Requesting authorization...")
            action_url = self.get_authorization_url(app_id)
            raise NotAuthorizedError(action_url)
        response.raise_for_status()
        return response.json()

    def get_authorization_url(self, app_id: str) -> str:
        """Get the authorization URL to connect an app.

        Args:
            app_id (str): The ID of the app to authorize.

        Returns:
            str: A message containing the authorization URL.

        Raises:
            HTTPError: If the API request fails.
        """
        response = self.client.post("/connections/authorize", json={"app_id": app_id})
        response.raise_for_status()
        url = response.json().get("authorize_url")
        return f"Please ask the user to visit the following url to authorize the application: {url}. Render the url in proper markdown format with a clickable link."

    def list_all_apps(self) -> list[dict[str, Any]]:
        """Fetch available apps from AgentR API.

        Returns:
            List[Dict[str, Any]]: A list of application data dictionaries.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        response = self.client.get("/apps/")
        response.raise_for_status()
        return response.json().get("items", [])

    def list_my_apps(self) -> list[dict[str, Any]]:
        """Fetch user apps from AgentR API.

        Returns:
            List[Dict[str, Any]]: A list of user app data dictionaries.
        """
        response = self.client.get("/apps/me/")
        response.raise_for_status()
        return response.json().get("items", [])

    def list_my_connections(self) -> list[dict[str, Any]]:
        """Fetch user connections from AgentR API.

        Returns:
            List[Dict[str, Any]]: A list of user connection data dictionaries.
        """
        response = self.client.get("/connections/")
        response.raise_for_status()
        return response.json().get("items", [])

    def get_app_details(self, app_id: str) -> dict[str, Any]:
        """Fetch a specific app from AgentR API.

        Args:
            app_id (str): ID of the app to fetch.

        Returns:
            dict: App configuration data.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        response = self.client.get(f"/apps/{app_id}")
        response.raise_for_status()
        return response.json()

    def list_all_tools(self) -> list[dict[str, Any]]:
        """List all available tools from the AgentR API.

        Note: In the backend, tools are globally listed and not tied to a
              specific app at this endpoint.

        Returns:
            List[Dict[str, Any]]: A list of tool configurations.
        """
        response = self.client.get("/tools/")
        response.raise_for_status()
        return response.json().get("items", [])

    def get_tool_details(self, tool_id: str) -> dict[str, Any]:
        """Fetch a specific tool configuration from the AgentR API.

        Args:
            tool_id (str): ID of the tool to fetch.

        Returns:
            dict: Tool configuration data.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        response = self.client.get(f"/tools/{tool_id}")
        response.raise_for_status()
        return response.json()

    def search_all_apps(self, query: str, limit: int = 2) -> list[dict[str, Any]]:
        """Search for apps from the AgentR API.

        Args:
            query (str): The query to search for.
            limit (int, optional): The number of apps to return. Defaults to 2.

        Returns:
            List[Dict[str, Any]]: A list of app data dictionaries.
        """
        response = self.client.get("/apps/", params={"search": query, "limit": limit})
        response.raise_for_status()
        return response.json().get("items", [])

    def search_all_tools(self, query: str, limit: int = 2) -> list[dict[str, Any]]:
        """Search for tools from the AgentR API.

        Args:
            query (str): The query to search for.
            limit (int, optional): The number of tools to return. Defaults to 2.
        """
        response = self.client.get("/tools/", params={"search": query, "limit": limit})
        response.raise_for_status()
        return response.json().get("items", [])
