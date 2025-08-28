from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

import requests

from .auth import AuthClient
from .errors import ApiError


BASE_URL = "https://connect.patsnap.com"


class HttpClient:
    """Lightweight HTTP client that injects auth and apikey automatically."""

    def __init__(
        self,
        auth: AuthClient,
        *,
        base_url: str = BASE_URL,
        session: Optional[requests.Session] = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._auth = auth
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._timeout = timeout_seconds

    def close(self) -> None:
        try:
            self._session.close()
        except Exception:
            pass

    def post_json(
        self,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self._base_url}/{path.lstrip('/')}"
        merged_headers: Dict[str, str] = {"Content-Type": "application/json"}
        merged_headers.update(self._auth.get_authorization_header())
        if headers:
            merged_headers.update(headers)

        merged_params: Dict[str, Any] = {"apikey": self._auth.client_id}
        if params:
            merged_params.update(params)

        response = self._session.post(
            url,
            headers=merged_headers,
            params=merged_params,
            json=json_body or {},
            timeout=self._timeout,
        )

        if response.status_code >= 400:
            raise ApiError(
                f"HTTP {response.status_code} calling {url}",
                status_code=response.status_code,
                response_text=response.text,
            )

        try:
            payload: Dict[str, Any] = response.json()
        except ValueError:
            raise ApiError("Response was not valid JSON", response_text=response.text)

        # Patsnap responses include status, error_code; surface errors consistently
        if not isinstance(payload, dict):
            raise ApiError("Response JSON was not an object", response_text=str(payload))

        status = payload.get("status")
        error_code = payload.get("error_code")
        if status is False or (isinstance(error_code, int) and error_code != 0):
            raise ApiError(
                payload.get("error_msg") or "API returned an error",
                status_code=response.status_code,
                error_code=error_code if isinstance(error_code, int) else None,
                response_text=response.text,
            )

        return payload

    def post(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Convenience method that delegates to post_json for JSON requests
        or handles multipart file uploads.
        
        Args:
            path: API endpoint path
            json: JSON data to send in request body
            params: Query parameters
            files: Files for multipart upload
            headers: Additional headers
            
        Returns:
            Dict containing the API response data
        """
        if files:
            # Handle multipart file upload
            url = f"{self._base_url}/{path.lstrip('/')}"
            merged_headers: Dict[str, str] = {}
            merged_headers.update(self._auth.get_authorization_header())
            if headers:
                merged_headers.update(headers)

            merged_params: Dict[str, Any] = {"apikey": self._auth.client_id}
            if params:
                merged_params.update(params)

            response = self._session.post(
                url,
                files=files,
                headers=merged_headers,
                params=merged_params,
                timeout=self._timeout,
            )

            # Parse and validate response
            try:
                payload = response.json()
            except ValueError as e:
                raise ApiError(f"Invalid JSON response: {e}", status_code=response.status_code, response_text=response.text)

            # Check for API errors
            status = payload.get("status")
            error_code = payload.get("error_code")
            if status is False or (isinstance(error_code, int) and error_code != 0):
                raise ApiError(
                    payload.get("error_msg") or "API returned an error",
                    status_code=response.status_code,
                    error_code=error_code if isinstance(error_code, int) else None,
                    response_text=response.text,
                )

            return payload
        else:
            # Delegate to post_json for regular JSON requests
            return self.post_json(path, json_body=json, headers=headers, params=params)


__all__ = ["HttpClient", "BASE_URL"]



