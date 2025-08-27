import json
import gzip
import zlib
import brotli
from typing import Dict, Any, Optional, Union


class Response:
    """Response object similar to requests.Response."""

    def __init__(
            self,
            status_code: int,
            headers: Dict[str, str],
            content: Union[str, bytes],
            url: str,
            request_headers: Dict[str, str],
            tls_version: str = "",
            cipher_suite: str = "",
            ja3_hash: str = ""
    ):
        self.status_code = status_code
        self.headers = headers
        self._raw_content = content
        self.url = url
        self.request = type('Request', (), {
            'headers': request_headers,
            'url': url
        })()

        # TLS info
        self.tls_version = tls_version
        self.cipher_suite = cipher_suite
        self.ja3_hash = ja3_hash

        # Decompress content if needed
        self._content = self._decompress_content()

        # Parse cookies
        self.cookies = self._parse_cookies()

    def _decompress_content(self) -> bytes:
        """Decompress content based on Content-Encoding header."""
        content = self._raw_content

        # Convert to bytes if it's a string
        if isinstance(content, str):
            content = content.encode('utf-8')

        # Get content encoding
        encoding = self.headers.get('content-encoding', '').lower()

        if not encoding:
            return content

        print(f"Debug: Trying to decompress {len(content)} bytes with {encoding}")
        print(f"Debug: First 20 bytes: {content[:20]}")

        try:
            if encoding == 'gzip':
                return gzip.decompress(content)
            elif encoding == 'deflate':
                # Try raw deflate first, then with zlib header
                try:
                    return zlib.decompress(content, -zlib.MAX_WBITS)
                except:
                    return zlib.decompress(content)
            elif encoding == 'br':
                # Try different brotli decompression methods
                try:
                    return brotli.decompress(content)
                except Exception as e1:
                    print(f"Debug: Standard brotli failed: {e1}")
                    # CRITICAL FIX: Check if it's actually uncompressed
                    try:
                        test_decode = content.decode('utf-8', errors='ignore')[:100]
                        if test_decode.startswith('{') or '<' in test_decode:
                            print("Debug: Content appears to be uncompressed despite header")
                            return content
                    except:
                        pass

                    # Try manual decompression with different parameters
                    try:
                        import brotlicffi
                        return brotlicffi.decompress(content)
                    except ImportError:
                        pass
                    except:
                        pass

                    # FORCE FALLBACK: Return content anyway for debugging
                    print(f"Debug: All brotli methods failed, returning raw content")
                    return content

            elif encoding == 'zstd':
                try:
                    import zstd
                    return zstd.decompress(content)
                except ImportError:
                    print("Warning: zstd decompression not available, install pyzstd")
                    return content
            else:
                print(f"Warning: Unknown content-encoding: {encoding}")
                return content
        except Exception as e:
            print(f"Warning: Failed to decompress content with {encoding}: {e}")
            print(f"Debug: Content length: {len(content)}")
            print(f"Debug: Content starts with: {content[:50]}")

            # FALLBACK: Return raw content for manual inspection
            return content

    @property
    def content(self) -> bytes:
        """Response content as bytes (decompressed)."""
        return self._content

    @property
    def text(self) -> str:
        """Response content as text (decompressed)."""
        # Try to detect encoding from headers
        content_type = self.headers.get('content-type', '')
        encoding = 'utf-8'  # default

        if 'charset=' in content_type:
            try:
                encoding = content_type.split('charset=')[-1].split(';')[0].strip()
            except:
                encoding = 'utf-8'

        try:
            return self._content.decode(encoding)
        except UnicodeDecodeError:
            # Fallback to utf-8 with error handling
            return self._content.decode('utf-8', errors='replace')

    def json(self) -> Any:
        """Parse response as JSON."""
        return json.loads(self.text)

    @property
    def ok(self) -> bool:
        """Returns True if status_code is less than 400."""
        return self.status_code < 400

    @property
    def is_redirect(self) -> bool:
        """Returns True if this response is a redirect."""
        return self.status_code in (301, 302, 303, 307, 308)

    @property
    def is_permanent_redirect(self) -> bool:
        """Returns True if this response is a permanent redirect."""
        return self.status_code in (301, 308)

    def raise_for_status(self):
        """Raises an HTTPError if status code indicates an error."""
        if not self.ok:
            from .exceptions import TlsClientError
            raise TlsClientError(f"HTTP {self.status_code} Error for URL: {self.url}")

    def _parse_cookies(self) -> Dict[str, str]:
        """Parse cookies from response headers - pragmatic approach."""
        cookies = {}

        set_cookie = self.headers.get('set-cookie', '')
        if not set_cookie:
            return cookies

        # Split by comma, but only if followed by a space and word character
        # This avoids splitting cookie values that contain commas
        import re
        cookie_parts = re.split(r',\s*(?=[a-zA-Z])', set_cookie)

        for cookie in cookie_parts:
            # Get only the name=value part (before first semicolon)
            main_part = cookie.split(';')[0].strip()
            if '=' in main_part:
                name, value = main_part.split('=', 1)
                cookies[name.strip()] = value.strip()

        return cookies

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}]>"

    def __bool__(self) -> bool:
        """Returns True if status_code is less than 400."""
        return self.ok