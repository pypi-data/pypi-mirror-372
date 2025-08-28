import requests
from gepeto.prompts import Prompts
from gepeto.agents import Agents
import os
from typing import Optional, List


class Gepeto:
    def __init__(self, api_key: Optional[str] = None, x_trace_id: Optional[str] = None):
        """Initialize Gepeto client with API key from env or passed directly"""
        self.api_key = api_key or os.environ.get("GEPETO_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEPETO_API_KEY must be set in environment or passed to constructor"
            )

        self.base_url = os.environ.get(
            "GEPETO_BASE_URL", "https://gateway.start248.com"
        )
        self.auth_url = os.environ.get(
            "GEPETO_AUTH_URL", f"{self.base_url}/auth/api/v1"
        )
        self.server_url = os.environ.get(
            "GEPETO_SERVER_URL", f"{self.base_url}/server/api/v1"
        )
        self.x_trace_id = x_trace_id

        # Authenticate with API
        # self.org_id = self._authenticate()
        self.prompts = Prompts(api_key=self.api_key, base_url=self.server_url)
        self.agents = Agents(
            api_key=self.api_key,
            base_url=self.server_url,
            prompts=self.prompts,
            x_trace_id=self.x_trace_id,
        )

    # def _authenticate(self):
    #     """Authenticate with the Gepeto API"""
    #     response = requests.post(
    #         "",  # URL to be filled in
    #         headers={"Authorization": f"Bearer {self.api_key}"}
    #     )
    #     response.raise_for_status()
    #     return response.json().get("organization_id")
