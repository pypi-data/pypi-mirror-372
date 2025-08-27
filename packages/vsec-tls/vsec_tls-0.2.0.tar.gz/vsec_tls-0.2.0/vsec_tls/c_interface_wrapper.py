import ctypes
import subprocess
from ctypes import Structure, c_char_p, c_int, c_uint16, c_uint64, c_uint32, POINTER
import json
import platform
import os
from pathlib import Path


# C-Strukturen definieren
class CResponse(Structure):
    _fields_ = [
        ("status", c_uint16),
        ("body", c_char_p),
        ("headers", c_char_p),
        ("tls_version", c_char_p),
        ("cipher_suite", c_char_p),
        ("ja3_hash", c_char_p),
        ("license_valid", c_int),
        ("license_info", c_char_p),
        ("client_hello_json", c_char_p),
        ("success", c_int),
        ("error_message", c_char_p),
    ]


class CLicenseInfo(Structure):
    _fields_ = [
        ("valid", c_int),
        ("customer_id", c_char_p),
        ("company_name", c_char_p),
        ("plan", c_char_p),
        ("expires", c_char_p),
        ("days_remaining", c_uint32),
        ("max_requests_per_day", c_uint64),
        ("daily_usage", c_uint64),
        ("remaining_requests_today", c_uint64),
        ("features_json", c_char_p),
        ("error_message", c_char_p),
    ]


class CRequestStatus(Structure):
    _fields_ = [
        ("requests_used_today", c_uint64),
        ("daily_limit", c_uint64),
        ("remaining_requests", c_uint64),
        ("success", c_int),
        ("error_message", c_char_p),
    ]


def _load_native():
    """Load the native C library."""
    base_dir = os.path.dirname(__file__)
    dep_dir = os.path.join(base_dir, "dependencies")
    deps_dir = Path(__file__).parent / "dependencies"

    system = platform.system()
    machine = platform.machine().lower()

    if system == "Windows": # Windows
        libname = "velum_secure.dll"
    elif system == "Darwin":  # macOS
        try:
            for dylib in deps_dir.glob("*.dylib"):
                subprocess.run(['xattr', '-d', 'com.apple.quarantine', str(dylib)],
                               capture_output=True, check=False, stderr=subprocess.DEVNULL)
        except:
            pass
        if machine == "x86_64":
            libname = "libvelum_secure_x86_64.dylib"
        elif machine in ("arm64", "aarch64"):
            libname = "libvelum_secure_arm64.dylib"
        else:
            raise OSError(f"Unsupported macOS architecture: {machine}")
    elif system == "Linux": # Linux
        libname = "libvelum_secure.so"
        try:
            os.chmod(libname, 0o755)
        except:
            pass
    else:
        raise OSError(f"Unsupported platform: {system}")

    libpath = os.path.join(dep_dir, libname)
    if not os.path.exists(libpath):
        raise FileNotFoundError(f"Native library not found: {libpath}")

    lib = ctypes.CDLL(libpath)

    # Funktionssignaturen definieren
    lib.velum_send_request.argtypes = [c_char_p, c_char_p]
    lib.velum_send_request.restype = POINTER(CResponse)

    lib.velum_validate_license.argtypes = [c_char_p, c_char_p]
    lib.velum_validate_license.restype = POINTER(CLicenseInfo)

    lib.velum_get_request_status.argtypes = [c_char_p, c_char_p]
    lib.velum_get_request_status.restype = POINTER(CRequestStatus)

    lib.velum_clear_cache.argtypes = [c_char_p, c_char_p]
    lib.velum_clear_cache.restype = c_int

    lib.velum_free_response.argtypes = [POINTER(CResponse)]
    lib.velum_free_response.restype = None

    lib.velum_free_license_info.argtypes = [POINTER(CLicenseInfo)]
    lib.velum_free_license_info.restype = None

    lib.velum_free_request_status.argtypes = [POINTER(CRequestStatus)]
    lib.velum_free_request_status.restype = None

    return lib


# Globale Library-Instanz
_native_lib = _load_native()


def _c_string(s):
    """Convert Python string to C string."""
    if s is None:
        return None
    return s.encode('utf-8')


def _py_string(c_str):
    """Convert C string to Python string."""
    if c_str is None or not c_str:
        return ""
    return c_str.decode('utf-8', errors='replace')


class VelumClient:
    """Wrapper for C library functions."""

    @staticmethod
    def send_request(profile_dict, url):
        """Send HTTP request via C library."""
        try:
            profile_json = json.dumps(profile_dict)
            profile_c = _c_string(profile_json)
            url_c = _c_string(url)

            # C-Funktion aufrufen
            c_response = _native_lib.velum_send_request(profile_c, url_c)

            if not c_response:
                raise RuntimeError("C library returned null response")

            response = c_response.contents

            # Fehlerbehandlung
            if not response.success:
                error_msg = _py_string(response.error_message)
                _native_lib.velum_free_response(c_response)
                raise RuntimeError(f"Request failed: {error_msg}")

            # Response-Daten extrahieren
            headers_str = _py_string(response.headers)
            license_info_str = _py_string(response.license_info)

            result = {
                "status": response.status,
                "body": _py_string(response.body),
                "headers": json.loads(headers_str) if headers_str else {},
                "tls_version": _py_string(response.tls_version),
                "cipher_suite": _py_string(response.cipher_suite),
                "ja3_hash": _py_string(response.ja3_hash),
                "license_valid": bool(response.license_valid),
                "license_info": license_info_str if license_info_str else None,
                "client_hello_json": _py_string(response.client_hello_json)
            }

            # Memory cleanup
            _native_lib.velum_free_response(c_response)

            return result

        except Exception as e:
            raise RuntimeError(f"C library error: {e}")

    @staticmethod
    def validate_license(license_key, api_key):
        """Validate license via C library."""
        try:
            license_key_c = _c_string(license_key)
            api_key_c = _c_string(api_key)

            c_license = _native_lib.velum_validate_license(license_key_c, api_key_c)

            if not c_license:
                raise RuntimeError("C library returned null license info")

            license_info = c_license.contents

            # Fehlerbehandlung
            if not license_info.valid:
                error_msg = _py_string(license_info.error_message)
                _native_lib.velum_free_license_info(c_license)
                raise RuntimeError(f"License validation failed: {error_msg}")

            # License-Daten extrahieren
            features_str = _py_string(license_info.features_json)
            features = json.loads(features_str) if features_str else []

            result = {
                "valid": True,
                "customer_id": _py_string(license_info.customer_id),
                "company_name": _py_string(license_info.company_name),
                "plan": _py_string(license_info.plan),
                "expires": _py_string(license_info.expires),
                "days_remaining": license_info.days_remaining,
                "max_requests_per_day": license_info.max_requests_per_day,
                "daily_usage": license_info.daily_usage,
                "remaining_requests_today": license_info.remaining_requests_today,
                "features": features
            }

            # Memory cleanup
            _native_lib.velum_free_license_info(c_license)

            return result

        except Exception as e:
            raise RuntimeError(f"License validation error: {e}")

    @staticmethod
    def get_request_status(license_key, api_key):
        """Get request status via C library."""
        try:
            license_key_c = _c_string(license_key)
            api_key_c = _c_string(api_key)

            c_status = _native_lib.velum_get_request_status(license_key_c, api_key_c)

            if not c_status:
                raise RuntimeError("C library returned null status")

            status = c_status.contents

            # Fehlerbehandlung
            if not status.success:
                error_msg = _py_string(status.error_message)
                _native_lib.velum_free_request_status(c_status)
                raise RuntimeError(f"Get request status failed: {error_msg}")

            result = {
                "requests_used_today": status.requests_used_today,
                "daily_limit": status.daily_limit,
                "remaining_requests": status.remaining_requests
            }

            # Memory cleanup
            _native_lib.velum_free_request_status(c_status)

            return result

        except Exception as e:
            raise RuntimeError(f"Request status error: {e}")

    @staticmethod
    def clear_cache(license_key, api_key):
        """Clear cache via C library."""
        try:
            license_key_c = _c_string(license_key)
            api_key_c = _c_string(api_key)

            result = _native_lib.velum_clear_cache(license_key_c, api_key_c)

            return bool(result)

        except Exception as e:
            raise RuntimeError(f"Clear cache error: {e}")


# Kompatibilitäts-Wrapper für alte API
class LegacyTlsClient:
    """Legacy wrapper to maintain old API compatibility."""

    @staticmethod
    def send_profiled_request_sync(profile, url):
        """Legacy sync request method."""
        return VelumClient.send_request(profile, url)

    @staticmethod
    def validate_license_py(license_key, api_key):
        """Legacy license validation method."""
        return VelumClient.validate_license(license_key, api_key)

    @staticmethod
    async def send_profiled_request_async_py(profile, url):
        """Legacy async request method - runs sync in thread pool."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, VelumClient.send_request, profile, url)


# Globale Instanz für Kompatibilität
_tls_client = LegacyTlsClient()