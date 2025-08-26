import requests
from typing import Dict, Any, Optional
from .errors import APIError, AuthError

class HTTPClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: float = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def post(self, path: str, json_body: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = self.session.post(url, headers=self._headers(), json=json_body, timeout=self.timeout)

        if resp.status_code == 401:
            raise AuthError("Unauthorized – check your PROTONX_API_KEY.")
        if not (200 <= resp.status_code < 300):
            raise APIError(resp.status_code, resp.text)

        return resp.json()
