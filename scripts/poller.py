# scripts/poller.py
"""
Wazuh Alert Poller
Handles authentication and alert retrieval from Wazuh REST API.
"""

import os
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings in lab environments
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)


class WazuhPoller:
    """
    Polls the Wazuh REST API for security alerts.
    
    Handles JWT authentication with automatic token refresh,
    configurable alert level filtering, and pagination.
    """
    
    # Wazuh JWT tokens expire at 900 seconds; refresh at 800 to be safe
    TOKEN_REFRESH_INTERVAL = 800

    def __init__(self, host: str, port: int, username: str, 
                 password: str, verify_ssl: bool = False):
        """
        Initialize the poller with Wazuh connection details.
        
        Args:
            host: Full URL of Wazuh manager (e.g., https://192.168.1.100)
            port: API port (default: 55000)
            username: Wazuh API username
            password: Wazuh API password
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = f"{host}:{port}"
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        
        self._token: Optional[str] = None
        self._token_acquired_at: Optional[float] = None
        
        logger.info(f"WazuhPoller initialized for {self.base_url}")

    def _get_token(self) -> str:
        """
        Acquire a JWT token from Wazuh API using Basic Auth.
        
        Returns:
            JWT token string
            
        Raises:
            ConnectionError: If Wazuh API is unreachable
            AuthenticationError: If credentials are invalid
        """
        auth_url = f"{self.base_url}/security/user/authenticate"
        
        try:
            response = requests.post(
                auth_url,
                auth=(self.username, self.password),
                verify=self.verify_ssl,
                timeout=30
            )
            response.raise_for_status()
            
            token = response.json()["data"]["token"]
            self._token_acquired_at = time.time()
            logger.debug("Wazuh API token acquired successfully")
            return token
            
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Cannot connect to Wazuh API at {self.base_url}. "
                f"Is Wazuh running? Error: {e}"
            )
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise PermissionError(
                    "Wazuh API authentication failed. "
                    "Check WAZUH_USER and WAZUH_PASSWORD in .env"
                )
            raise

    def _get_valid_token(self) -> str:
        """Return a valid token, refreshing if approaching expiry."""
        if (self._token is None or 
            self._token_acquired_at is None or
            time.time() - self._token_acquired_at > self.TOKEN_REFRESH_INTERVAL):
            self._token = self._get_token()
        return self._token

    def fetch_alerts(self, 
                     min_level: int = 7,
                     limit: int = 10,
                     hours_back: int = 1) -> List[Dict]:
        """
        Retrieve security alerts from Wazuh API.
        
        Args:
            min_level: Minimum Wazuh rule level (1-15)
            limit: Maximum number of alerts to return
            hours_back: How far back to look for alerts (hours)
            
        Returns:
            List of normalized alert dictionaries
        """
        token = self._get_valid_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Calculate time window
        since = (datetime.utcnow() - timedelta(hours=hours_back)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        
        params = {
            "level": min_level,
            "limit": limit,
            "sort": "-timestamp",
            "timestamp": f">{since}"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/security/events",
                headers=headers,
                params=params,
                verify=self.verify_ssl,
                timeout=30
            )
            response.raise_for_status()
            
            alerts = response.json().get("data", {}).get("affected_items", [])
            logger.info(f"Retrieved {len(alerts)} alerts (level>={min_level})")
            return alerts
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                # Token might have expired despite our refresh logic; retry once
                self._token = None
                return self.fetch_alerts(min_level, limit, hours_back)
            logger.error(f"Wazuh API error: {e}")
            return []

    def test_connection(self) -> Dict:
        """
        Test Wazuh API connectivity and return version info.
        
        Returns:
            Dict with connection status and Wazuh version
        """
        try:
            response = requests.get(
                f"{self.base_url}/",
                verify=self.verify_ssl,
                timeout=10
            )
            data = response.json().get("data", {})
            return {
                "connected": True,
                "version": data.get("api_version", "unknown"),
                "title": data.get("title", "Wazuh API")
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}