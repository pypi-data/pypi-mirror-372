import json as js
from typing import Union, List
from urllib.parse import urlparse
from .exceptions import TlsClientError
from .response import Response
from .utils import prepare_body, guess_content_type
from .profiles import get_profile
from .c_interface_wrapper import _tls_client
from typing import Optional, Dict, Any


class TlsSession:
    """Session object for persistent connections with cookie handling."""

    def __init__(
            self,
            license_key: str,
            api_key: str,
            ja3: Optional[str] = None,
            alpn: Optional[List[str]] = None,
            proxy: Optional[Dict[str, Any]] = None,
            http2_settings: Optional[Dict[str, Any]] = None,
            tls_padding: Optional[int] = None,
            headers: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = 30.0,
            verify: bool = True,
            default_profile: str = "chrome_139_windows",
            **kwargs
    ):
        """Initialize a TLS session."""
        # License validation
        if not license_key or not api_key:
            raise TlsClientError("license_key and api_key are required for Velum Secure")

        self.license_key = license_key
        self.api_key = api_key

        try:
            # Verwende neue C-Library API
            license_result = _tls_client.validate_license_py(license_key, api_key)
            self.license_info = license_result
            #print(f"Velum Secure license validated - Plan: {license_result.get('plan', 'unknown')}, "
            #      f"Days remaining: {license_result.get('days_remaining', 0)}")
        except Exception as e:
            raise TlsClientError(f"License validation failed: {e}")

        # Get default profile if no custom settings provided
        if not any([ja3, alpn, headers]):
            profile = get_profile(default_profile)
            self.ja3 = profile["ja3"]
            self.alpn = profile["alpn"]
            self.default_headers = profile["http_headers"].copy()
            self.http2_settings = http2_settings or profile.get("http2_settings")
        else:
            raise Exception('No suitable profile selected')

        self.proxy = proxy
        self.tls_padding = tls_padding
        self.timeout = timeout
        self.verify = verify

        # Session headers
        self.headers = self.default_headers.copy()
        if headers:
            self.headers.update(headers)

        # Cookie management
        self.cookies = {}
        if cookies:
            self.cookies.update(cookies)

        # Build base profile
        self._base_profile = self._build_profile()

    def _build_profile(self) -> Dict[str, Any]:
        """Build the base profile for requests."""
        profile = {
            "ja3": self.ja3,
            "alpn": self.alpn,
            "http_headers": self.headers.copy(),
            "license_key": self.license_key,
            "api_key": self.api_key,
            "timeout": self.timeout
        }

        if self.proxy:
            profile["proxy"] = self.proxy
        if self.http2_settings:
            profile["http2_settings"] = self.http2_settings
        if self.tls_padding is not None:
            profile["tls_padding"] = self.tls_padding

        return profile

    def _prepare_cookies(self, url: str) -> str:
        """Prepare cookie header for the request."""
        if not self.cookies:
            return ""

        cookie_parts = [f"{k}={v}" for k, v in self.cookies.items()]
        return "; ".join(cookie_parts)

    def _update_cookies(self, response_headers: Dict[str, str]):
        """Update cookies from response headers."""
        set_cookie = response_headers.get("set-cookie", "")
        if not set_cookie:
            return

        for cookie in set_cookie.split(","):
            parts = cookie.split(";")[0].split("=", 1)
            if len(parts) == 2:
                key, value = parts
                self.cookies[key.strip()] = value.strip()

    def request(
            self,
            method: str,
            url: str,
            headers: Optional[Dict[str, str]] = None,
            data: Optional[Union[str, bytes, dict]] = None,
            json: Optional[dict] = None,
            params: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = None,
            allow_redirects: bool = True,
            **kwargs
    ) -> Response:
        """Make a request."""
        # Build URL with params
        if params:
            parsed = urlparse(url)
            query_parts = []
            if parsed.query:
                query_parts.append(parsed.query)
            query_parts.extend([f"{k}={v}" for k, v in params.items()])
            url = url.split("?")[0] + "?" + "&".join(query_parts)

        # Prepare request profile
        profile = self._base_profile.copy()
        profile["method"] = method.upper()

        # Merge headers
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        # Handle cookies
        request_cookies = self.cookies.copy()
        if cookies:
            request_cookies.update(cookies)

        if request_cookies:
            cookie_header = "; ".join([f"{k}={v}" for k, v in request_cookies.items()])
            request_headers["cookie"] = cookie_header

        # Handle body
        body = data
        if json is not None:
            body = json
            request_headers["content-type"] = "application/json"

        if body is not None:
            profile["body"] = prepare_body(body)
            if "content-type" not in request_headers:
                request_headers["content-type"] = guess_content_type(body)

        profile["http_headers"] = request_headers

        # Make request - C-LIBRARY API
        try:
            raw_response = _tls_client.send_profiled_request_sync(profile, url)

            # Create response object
            response = Response(
                status_code=raw_response["status"],
                headers=raw_response["headers"],
                content=raw_response["body"],
                url=url,
                request_headers=request_headers,
                tls_version=raw_response.get("tls_version", ""),
                cipher_suite=raw_response.get("cipher_suite", ""),
                ja3_hash=raw_response.get("ja3_hash", "")
            )

            # License information
            response.license_valid = raw_response.get("license_valid", False)
            if raw_response.get("license_info"):
                response.license_info = js.loads(raw_response["license_info"]) if isinstance(raw_response["license_info"], str) else raw_response["license_info"]
            else:
                response.license_info = None

            # Update session cookies
            self._update_cookies(response.headers)

            # Handle redirects
            if allow_redirects and response.is_redirect:
                location = response.headers.get("location")
                if location:
                    if not location.startswith(("http://", "https://")):
                        parsed = urlparse(url)
                        location = f"{parsed.scheme}://{parsed.netloc}{location}"
                    return self.request(method="GET", url=location, allow_redirects=True)

            return response

        except Exception as e:
            raise TlsClientError(f"Request failed: {e}")

    async def request_async(
            self,
            method: str,
            url: str,
            headers: Optional[Dict[str, str]] = None,
            data: Optional[Union[str, bytes, dict]] = None,
            json: Optional[dict] = None,
            params: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = None,
            allow_redirects: bool = True,
            **kwargs
    ) -> Response:
        """Async version of request."""
        # Build URL with params
        if params:
            parsed = urlparse(url)
            query_parts = []
            if parsed.query:
                query_parts.append(parsed.query)
            query_parts.extend([f"{k}={v}" for k, v in params.items()])
            url = url.split("?")[0] + "?" + "&".join(query_parts)

        # Prepare request profile
        profile = self._base_profile.copy()
        profile["method"] = method.upper()

        # Merge headers
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        # Handle cookies
        request_cookies = self.cookies.copy()
        if cookies:
            request_cookies.update(cookies)

        if request_cookies:
            cookie_header = "; ".join([f"{k}={v}" for k, v in request_cookies.items()])
            request_headers["cookie"] = cookie_header

        # Handle body
        body = data
        if json is not None:
            body = json
            request_headers["content-type"] = "application/json"

        if body is not None:
            profile["body"] = prepare_body(body)
            if "content-type" not in request_headers:
                request_headers["content-type"] = guess_content_type(body)

        profile["http_headers"] = request_headers

        # Make request - C-LIBRARY API
        try:
            raw_response = await _tls_client.send_profiled_request_async_py(profile, url)

            # Create response object
            response = Response(
                status_code=raw_response["status"],
                headers=raw_response["headers"],
                content=raw_response["body"],
                url=url,
                request_headers=request_headers,
                tls_version=raw_response.get("tls_version", ""),
                cipher_suite=raw_response.get("cipher_suite", ""),
                ja3_hash=raw_response.get("ja3_hash", "")
            )

            # License information
            response.license_valid = raw_response.get("license_valid", False)
            if raw_response.get("license_info"):
                response.license_info = js.loads(raw_response["license_info"]) if isinstance(raw_response["license_info"], str) else raw_response["license_info"]
            else:
                response.license_info = None

            # Update session cookies
            self._update_cookies(response.headers)

            # Handle redirects
            if allow_redirects and response.is_redirect:
                location = response.headers.get("location")
                if location:
                    if not location.startswith(("http://", "https://")):
                        parsed = urlparse(url)
                        location = f"{parsed.scheme}://{parsed.netloc}{location}"
                    return await self.request_async(method="GET", url=location, allow_redirects=True)

            return response

        except Exception as e:
            raise TlsClientError(f"Request failed: {e}")

    # Convenience methods
    def get(self, url: str, **kwargs) -> Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> Response:
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs) -> Response:
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs) -> Response:
        return self.request("DELETE", url, **kwargs)

    def head(self, url: str, **kwargs) -> Response:
        return self.request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs) -> Response:
        return self.request("OPTIONS", url, **kwargs)

    # Async convenience methods
    async def get_async(self, url: str, **kwargs) -> Response:
        return await self.request_async("GET", url, **kwargs)

    async def post_async(self, url: str, **kwargs) -> Response:
        return await self.request_async("POST", url, **kwargs)

    async def put_async(self, url: str, **kwargs) -> Response:
        return await self.request_async("PUT", url, **kwargs)

    async def patch_async(self, url: str, **kwargs) -> Response:
        return await self.request_async("PATCH", url, **kwargs)

    async def delete_async(self, url: str, **kwargs) -> Response:
        return await self.request_async("DELETE", url, **kwargs)