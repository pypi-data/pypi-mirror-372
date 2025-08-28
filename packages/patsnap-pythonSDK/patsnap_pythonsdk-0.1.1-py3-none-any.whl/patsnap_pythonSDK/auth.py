from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any, Dict, Optional

import requests

from .errors import AuthError


DEFAULT_TOKEN_URL = "https://connect.patsnap.com/oauth/token"


@dataclass
class _TokenState:
    token: Optional[str] = None
    expires_at_utc: Optional[datetime] = None


class AuthClient:
    """Client-credentials OAuth helper for Patsnap API.

    - Obtains a bearer token using HTTP Basic auth with Client ID and Secret
    - Caches the token until it is close to expiry, then refreshes automatically
    - Thread-safe

    Usage:
        auth = AuthClient(client_id, client_secret)
        headers = {"Authorization": auth.get_authorization_value()}
        # Also pass apikey as query param in business API calls: apikey=client_id
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        token_url: str = DEFAULT_TOKEN_URL,
        session: Optional[requests.Session] = None,
        timeout_seconds: float = 15.0,
        refresh_leeway_seconds: int = 60,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url
        self._timeout_seconds = timeout_seconds
        self._refresh_leeway = max(0, int(refresh_leeway_seconds))

        self._session = session or requests.Session()
        self._lock = Lock()
        self._state = _TokenState()

    @property
    def client_id(self) -> str:
        return self._client_id

    def close(self) -> None:
        """Close the underlying HTTP session if we created it."""
        try:
            self._session.close()
        except Exception:
            # Best-effort; do not propagate errors on close
            pass

    # ------------------------ Public API ------------------------
    def get_token(self, *, force_refresh: bool = False) -> str:
        """Return a valid bearer token, refreshing if needed."""
        with self._lock:
            if force_refresh or not self._is_token_valid_locked():
                self._fetch_new_token_locked()
            assert self._state.token is not None  # for type-checkers
            return self._state.token

    def get_authorization_value(self, *, force_refresh: bool = False) -> str:
        """Return the value for the Authorization header: "Bearer <token>"."""
        token = self.get_token(force_refresh=force_refresh)
        return f"Bearer {token}"

    def get_authorization_header(self, *, force_refresh: bool = False) -> Dict[str, str]:
        """Return a dict with the Authorization header set."""
        return {"Authorization": self.get_authorization_value(force_refresh=force_refresh)}

    # --------------------- Internal helpers ---------------------
    def _is_token_valid_locked(self) -> bool:
        token = self._state.token
        expires_at = self._state.expires_at_utc
        if not token or not expires_at:
            return False
        # Refresh slightly before actual expiry
        now_utc = datetime.now(timezone.utc)
        return now_utc < expires_at

    def _fetch_new_token_locked(self) -> None:
        data = {"grant_type": "client_credentials"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Try the standard OAuth approach first
        try:
            response = self._session.post(
                self._token_url,
                data=data,
                headers=headers,
                auth=(self._client_id, self._client_secret),
                timeout=self._timeout_seconds,
            )
            
            # If that fails with auth error, try the Patsnap URL-based auth format
            if response.status_code == 401 or (response.status_code == 200 and 
                response.json().get("error_code") == 67200003):
                # Try URL-based authentication as fallback
                auth_url = f"https://{self._client_id}:{self._client_secret}@{self._token_url.replace('https://', '')}"
                response = self._session.post(
                    auth_url,
                    data=data,
                    headers=headers,
                    timeout=self._timeout_seconds,
                )
        except requests.RequestException as exc:
            # Try URL-based authentication as fallback
            try:
                auth_url = f"https://{self._client_id}:{self._client_secret}@{self._token_url.replace('https://', '')}"
                response = self._session.post(
                    auth_url,
                    data=data,
                    headers=headers,
                    timeout=self._timeout_seconds,
                )
            except requests.RequestException:
                raise AuthError(f"Failed to reach token endpoint: {exc}")

        if response.status_code >= 400:
            raise AuthError(
                f"Token endpoint returned HTTP {response.status_code}: {response.text}",
                status_code=response.status_code,
            )

        try:
            payload: Dict[str, Any] = response.json()
        except ValueError:
            raise AuthError("Token endpoint did not return JSON.")

        # Handle multiple Patsnap response formats:
        # Format 1: { token, token_type, expires_in, status, issued_at }
        # Format 2: { data: { token }, ... }
        # Format 3: Standard OAuth { access_token, ... }
        token = None
        if "data" in payload and isinstance(payload["data"], dict):
            token = payload["data"].get("token")
        if not token:
            token = payload.get("token") or payload.get("access_token")
        
        if not token or not isinstance(token, str):
            raise AuthError("Token missing in response.")

        expires_in = _coerce_int(payload.get("expires_in"))
        issued_at_ms = _coerce_int(payload.get("issued_at"))

        now_utc = datetime.now(timezone.utc)
        if expires_in is not None and issued_at_ms is not None:
            issued_at = datetime.fromtimestamp(issued_at_ms / 1000.0, tz=timezone.utc)
            raw_expires_at = issued_at + timedelta(seconds=expires_in)
        elif expires_in is not None:
            raw_expires_at = now_utc + timedelta(seconds=expires_in)
        else:
            # Fallback to 30 minutes as per docs
            raw_expires_at = now_utc + timedelta(minutes=30)

        # Apply leeway for proactive refreshes
        expires_at_with_leeway = raw_expires_at - timedelta(seconds=self._refresh_leeway)
        # Never set expiry earlier than now + 1 second
        min_valid_until = now_utc + timedelta(seconds=1)
        if expires_at_with_leeway <= min_valid_until:
            expires_at_with_leeway = min_valid_until

        self._state.token = token
        self._state.expires_at_utc = expires_at_with_leeway


def _coerce_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


__all__ = ["AuthClient"]


