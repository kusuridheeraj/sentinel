import httpx
import logging
import json
from typing import Optional, Dict, Any

# Configure a silent logger by default to avoid spamming user apps
logger = logging.getLogger("sentinel-sdk")
logger.addHandler(logging.NullHandler())

class SentinelClient:
    def __init__(self, base_url: str, api_key: str, org_id: str, fail_silent: bool = True):
        """
        Initializes the Sentinel Client.
        
        :param base_url: URL of your Sentinel Server (e.g. "http://localhost:8000")
        :param api_key: Your API Key (Not used in PoC yet, but ready for future)
        :param org_id: Your Organization ID
        :param fail_silent: If True, connection errors won't crash your app (recommended).
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.org_id = org_id
        self.fail_silent = fail_silent
        self.headers = {
            "X-Sentinel-Key": api_key,
            "Content-Type": "application/json"
        }

    def log(self, actor: str, action: str, resource: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Synchronous logging. Best for scripts or background jobs.
        """
        payload = {
            "org_id": self.org_id,
            "actor_id": actor,
            "action": action,
            "resource": resource,
            "context": context or {}
        }
        
        try:
            # We use params for the PoC endpoint because the API was designed with query params initially
            # In V2, we should move this to JSON body.
            # Adapting to current API:
            response = httpx.post(
                f"{self.base_url}/audit/log", 
                params={
                    "org_id": self.org_id,
                    "actor_id": actor,
                    "action": action,
                    "resource": resource
                },
                headers=self.headers,
                timeout=2.0 
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send audit log: {e}")
            if not self.fail_silent:
                raise e
            return False

    async def alog(self, actor: str, action: str, resource: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Asynchronous logging. Best for FastAPI/Django/Node apps.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/audit/log", 
                    params={
                        "org_id": self.org_id,
                        "actor_id": actor,
                        "action": action,
                        "resource": resource
                    },
                    headers=self.headers,
                    timeout=2.0
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to send async audit log: {e}")
            if not self.fail_silent:
                raise e
            return False
