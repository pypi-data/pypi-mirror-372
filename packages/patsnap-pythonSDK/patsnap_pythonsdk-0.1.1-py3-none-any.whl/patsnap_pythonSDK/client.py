from __future__ import annotations

from typing import Optional

import requests

from .auth import AuthClient
from .http import HttpClient
from .namespaces import AnalyticsNamespace, PatentsNamespace


class PatsnapClient:
    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        base_url: str = "https://connect.patsnap.com",
        session: Optional[requests.Session] = None,
    ) -> None:
        self._auth = AuthClient(client_id, client_secret, token_url=f"{base_url.rstrip('/')}/oauth/token", session=session)
        self._http = HttpClient(self._auth, base_url=base_url, session=session)

        # Namespaces
        self.analytics = AnalyticsNamespace(self._http)
        self.patents = PatentsNamespace(self._http)

    def close(self) -> None:
        self._http.close()
        self._auth.close()


__all__ = ["PatsnapClient"]



