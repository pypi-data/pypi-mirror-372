import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx
from loguru import logger as log
from pickleclass import PickleClass


@dataclass
class SimpleAPIResponse:
    status: int
    method: str
    headers: dict
    body: Any


class SimpleAPI(PickleClass):
    def __init__(self, base_url: str, headers: Optional[Dict] = None, cache: bool = True):
        PickleClass.__init__(
            self
        )
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.cache_enabled = cache
        self.cache: Dict[str, SimpleAPIResponse] = {}

    def __repr__(self):
        return f"[{self.__class__.__name__}]"

    def _build_path(self, path: str = "") -> str:
        """Build the full request path"""
        if path.startswith('http'):
            return path
        return f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url

    def _check_cache(self, path: str, method: str, force_refresh: bool) -> Optional[SimpleAPIResponse]:
        """Check cache for existing response"""
        if force_refresh or not self.cache_enabled:
            return None

        cache_key = f"{method.upper()}:{path}"
        if cache_key in self.cache:
            log.debug(f"{self}: Cache hit for {method.upper()} {path}")
            return self.cache[cache_key]
        return None

    def _make_response(self, httpx_response, method: str) -> SimpleAPIResponse:
        """Convert httpx response to our Response object"""
        try:
            content_type = httpx_response.headers.get("Content-Type", "")

            if not httpx_response.content:
                content = ""
            elif "json" in content_type:
                try:
                    content = httpx_response.json()
                except (ValueError, json.JSONDecodeError):
                    content = httpx_response.text
            else:
                content = httpx_response.text
        except Exception as e:
            log.warning(f"{self}: Response decode error: {e}")
            raise

        return SimpleAPIResponse(
            status=httpx_response.status_code,
            method=method,
            headers=dict(httpx_response.headers),
            body=content,
        )

    def request(self, method: str, path: str = "", force_refresh: bool = False,
                headers: Optional[Dict] = None, **kwargs) -> SimpleAPIResponse:
        """Make synchronous HTTP request"""
        full_path = self._build_path(path)
        method = method.lower()

        log.info(f"{self}: {method.upper()} request to {full_path}")

        # Check cache first
        if cached := self._check_cache(full_path, method, force_refresh):
            return cached

        # Merge headers
        request_headers = {**self.headers}
        if headers:
            request_headers.update(headers)

        # Make request
        with httpx.Client(headers=request_headers) as client:
            response = client.request(method.upper(), full_path, **kwargs)

        # Create response object
        result = self._make_response(response, method)

        # Cache if enabled
        if self.cache_enabled:
            cache_key = f"{method.upper()}:{full_path}"
            self.cache[cache_key] = result

        return result

    async def async_request(self, method: str, path: str = "", force_refresh: bool = False,
                            headers: Optional[Dict] = None, **kwargs) -> SimpleAPIResponse:
        """Make asynchronous HTTP request"""
        full_path = self._build_path(path)
        method = method.lower()

        log.info(f"{self}: {method.upper()} request to {full_path}")

        # Check cache first
        if cached := self._check_cache(full_path, method, force_refresh):
            return cached

        # Merge headers
        request_headers = {**self.headers}
        if headers:
            request_headers.update(headers)

        # Make request
        async with httpx.AsyncClient(headers=request_headers) as client:
            response = await client.request(method.upper(), full_path, **kwargs)

        # Create response object
        result = self._make_response(response, method)

        # Cache if enabled
        if self.cache_enabled:
            cache_key = f"{method.upper()}:{full_path}"
            self.cache[cache_key] = result

        return result
