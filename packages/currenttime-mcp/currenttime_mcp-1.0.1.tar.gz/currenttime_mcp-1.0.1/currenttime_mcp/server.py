#!/usr/bin/env python3
"""
CurrentTime MCP Server
Provides accurate current time with IP-based timezone detection
"""

import logging
import os
from datetime import datetime
from ipaddress import ip_address
from typing import Any, Dict, Optional

try:
    # Prefer standard library zoneinfo on Python 3.9+
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # type: ignore
    _USE_ZONEINFO = True
except Exception:  # pragma: no cover - fallback path
    ZoneInfo = None  # type: ignore
    ZoneInfoNotFoundError = Exception  # type: ignore
    _USE_ZONEINFO = False

import pytz
import requests
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP("CurrentTime")

# Shared HTTP session with an identifying User-Agent
_session = requests.Session()
_session.headers.update(
    {
        "User-Agent": f"currenttime-mcp/1.0.1 (+https://github.com/currenttime-mcp/currenttime-mcp)",
        "Accept": "application/json",
    }
)

IPAPI_BASE = os.environ.get("IPAPI_BASE", "https://ipapi.co")
IPAPI_KEY = os.environ.get("IPAPI_KEY")  # optional key for higher rate limits


def _resolve_timezone(name: str):
    """Return a tzinfo for the given timezone name with graceful fallback.

    Uses zoneinfo when available, otherwise falls back to pytz.
    """
    if not name:
        return pytz.UTC if not _USE_ZONEINFO else ZoneInfo("UTC")
    try:
        if _USE_ZONEINFO:
            return ZoneInfo(name)
        return pytz.timezone(name)
    except (ZoneInfoNotFoundError, pytz.UnknownTimeZoneError):
        # Fallback to UTC on unknown timezone values
        return pytz.UTC if not _USE_ZONEINFO else ZoneInfo("UTC")


def _now_in_tz(tz):
    return datetime.now(tz)


def _fetch_ip_data(client_ip: Optional[str]) -> Dict[str, Any]:
    """Fetch JSON from ipapi.co, validating IP and handling payload errors.

    Returns the parsed JSON payload. Raises requests.RequestException on network/HTTP errors.
    """
    if client_ip:
        try:
            # Validate input is a real IP (prevents path tricks and clarifies behavior)
            ip_address(client_ip)
        except ValueError:
            return {
                "error": True,
                "reason": "Invalid IP address format",
            }
        url = f"{IPAPI_BASE}/{client_ip}/json/"
    else:
        url = f"{IPAPI_BASE}/json/"

    params = {}
    if IPAPI_KEY:
        params["key"] = IPAPI_KEY

    resp = _session.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # ipapi may return HTTP 200 with an error payload
    if isinstance(data, dict) and data.get("error"):
        # Normalize into a consistent error shape for callers
        return {
            "error": True,
            "reason": data.get("reason") or data.get("message") or "Unknown ipapi error",
        }
    return data  # type: ignore[return-value]


@mcp.tool()
def get_current_time(client_ip: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the current time with automatic timezone detection based on IP address.
    
    Args:
        client_ip: Optional IP address. If not provided, will detect automatically.
        
    Returns:
        Dictionary containing current time, timezone, and location info
    """
    try:
        location_data = _fetch_ip_data(client_ip)
        if isinstance(location_data, dict) and location_data.get("error"):
            raise requests.RequestException(location_data.get("reason", "ipapi error"))

        timezone_name = (location_data.get("timezone") if isinstance(location_data, dict) else None) or "UTC"
        tz = _resolve_timezone(timezone_name)
        current_time = _now_in_tz(tz)

        return {
            "success": True,
            "current_time": current_time.isoformat(),
            "timezone": timezone_name,
            "utc_offset": current_time.strftime("%z"),
            "formatted_time": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "timestamp": current_time.timestamp(),
            "location": {
                "city": location_data.get("city") if isinstance(location_data, dict) else None,
                "region": location_data.get("region") if isinstance(location_data, dict) else None,
                "country": location_data.get("country_name") if isinstance(location_data, dict) else None,
                "country_code": location_data.get("country_code") if isinstance(location_data, dict) else None,
                "ip": location_data.get("ip") if isinstance(location_data, dict) else None,
            },
            "is_dst": bool(current_time.dst()),
        }

    except requests.RequestException as e:
        logger.error(f"Network or API error: {e}")
        utc_tz = pytz.UTC if not _USE_ZONEINFO else ZoneInfo("UTC")
        utc_time = _now_in_tz(utc_tz)
        return {
            "success": False,
            "error": "Could not detect timezone, using UTC",
            "current_time": utc_time.isoformat(),
            "timezone": "UTC",
            "utc_offset": "+0000",
            "formatted_time": utc_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "timestamp": utc_time.timestamp(),
        }

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": str(e),
            "current_time": None,
        }


@mcp.tool()
def get_time_for_timezone(timezone_name: str) -> Dict[str, Any]:
    """
    Get the current time for a specific timezone.
    
    Args:
        timezone_name: Timezone name (e.g., 'America/New_York', 'Asia/Seoul', 'Europe/London')
        
    Returns:
        Dictionary containing current time for the specified timezone
    """
    try:
        tz = _resolve_timezone(timezone_name)
        current_time = _now_in_tz(tz)

        return {
            "success": True,
            "current_time": current_time.isoformat(),
            "timezone": timezone_name,
            "utc_offset": current_time.strftime("%z"),
            "formatted_time": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "timestamp": current_time.timestamp(),
            "is_dst": bool(current_time.dst()),
        }

    except Exception as e:
        # This will generally only trigger for severe internal errors now
        logger.error(f"Error getting time for timezone {timezone_name}: {e}")
        return {
            "success": False,
            "error": f"Unknown or invalid timezone: {timezone_name}",
        }


@mcp.tool()
def get_client_info(client_ip: Optional[str] = None) -> Dict[str, Any]:
    """
    Get client location and timezone information based on IP address.
    
    Args:
        client_ip: Optional IP address. If not provided, will detect automatically.
        
    Returns:
        Dictionary containing client location and timezone info
    """
    try:
        data = _fetch_ip_data(client_ip)
        if isinstance(data, dict) and data.get("error"):
            raise requests.RequestException(data.get("reason", "ipapi error"))

        return {
            "success": True,
            "ip": data.get("ip"),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country_name"),
            "country_code": data.get("country_code"),
            "timezone": data.get("timezone"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "postal": data.get("postal"),
            "calling_code": data.get("calling_code"),
            "currency": data.get("currency"),
            "languages": data.get("languages"),
            "asn": data.get("asn"),
            "org": data.get("org"),
        }

    except requests.RequestException as e:
        logger.error(f"Network or API error: {e}")
        return {
            "success": False,
            "error": "Could not retrieve client information",
            "details": str(e),
        }

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def list_common_timezones() -> Dict[str, Any]:
    """
    Get a list of common timezones grouped by region.
    
    Returns:
        Dictionary containing common timezones organized by region
    """
    common_timezones = {
        "America": [
            "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
            "America/Toronto", "America/Vancouver", "America/Mexico_City", "America/Sao_Paulo",
            "America/Buenos_Aires", "America/Lima", "America/Bogota"
        ],
        "Europe": [
            "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Rome", 
            "Europe/Madrid", "Europe/Amsterdam", "Europe/Stockholm", "Europe/Moscow",
            "Europe/Istanbul", "Europe/Athens"
        ],
        "Asia": [
            "Asia/Tokyo", "Asia/Seoul", "Asia/Shanghai", "Asia/Hong_Kong",
            "Asia/Singapore", "Asia/Bangkok", "Asia/Mumbai", "Asia/Dubai",
            "Asia/Jakarta", "Asia/Manila"
        ],
        "Australia": [
            "Australia/Sydney", "Australia/Melbourne", "Australia/Perth", "Australia/Brisbane",
            "Australia/Adelaide", "Australia/Darwin"
        ],
        "Africa": [
            "Africa/Cairo", "Africa/Lagos", "Africa/Johannesburg", "Africa/Nairobi",
            "Africa/Casablanca", "Africa/Tunis"
        ],
        "UTC": ["UTC"]
    }
    
    return {
        "success": True,
        "common_timezones": common_timezones,
        "total_available": len(pytz.all_timezones),
        "note": "Use get_time_for_timezone() with any of these timezone names"
    }


def main():
    """Main entry point for the MCP server."""
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
