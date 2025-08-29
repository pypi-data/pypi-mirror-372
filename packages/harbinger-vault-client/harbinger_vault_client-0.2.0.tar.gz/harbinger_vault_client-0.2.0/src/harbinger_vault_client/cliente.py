import os
import time
import json
import uuid
import random
import threading
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ContainerNameError(Exception):
    """Raised when the container name is not properly set."""
    pass


class VaultClient:
    def __init__(
        self,
        vault_url: str,
        auth_token: str,
        *,
        # Optional tuning knobs. Defaults are safe and enabled.
        session: Optional[Session] = None,
        timeout: Union[float, Tuple[float, float]] = 10.0,   # keep legacy default
        env_var_name: str = "VAULT_CLIENT_CONTAINER_NAME",
        retries_total: int = 6,                    # More retries for transient failures
        retries_backoff_factor: float = 1.5,           # More aggressive backoff
        retries_statuses: Optional[List[int]] = None,
        pool_connections: int = 200,
        pool_maxsize: int = 200,
        pool_block: bool = True,
        max_in_flight: Optional[int] = 30,                   # Lower concurrency ceiling
        rate_limit_per_sec: Optional[float] = 15.0,          # Default rate limiting to prevent overload
        rate_limit_burst: int = 10,                          # Smaller burst to be gentler on server
        use_idempotency_key: bool = True,
        idempotency_namespace: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000001"),
    ):
        self.vault_url = vault_url.rstrip("/")
        self.auth_token = auth_token
        self.error: Optional[str] = None
        self.container_name: Optional[str] = None

        self.env_var_name = env_var_name
        self.timeout = timeout
        self.use_idempotency_key = use_idempotency_key
        self.idempotency_namespace = idempotency_namespace

        self.session = session or self._build_session(
            retries_total=retries_total,
            backoff=retries_backoff_factor,
            statuses=retries_statuses or [401, 429, 500, 502, 503, 504],  # Include 401 for auth failures!
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            pool_block=pool_block,
        )

        # Optional client side controls, enabled by default
        self._sema: Optional[threading.BoundedSemaphore] = (
            threading.BoundedSemaphore(max_in_flight) if max_in_flight and max_in_flight > 0 else None
        )
        self._bucket: Optional[_TokenBucket] = (
            _TokenBucket(rate_limit_per_sec, rate_limit_burst)
            if rate_limit_per_sec and rate_limit_per_sec > 0
            else None
        )

        try:
            self.container_name = self._get_container_name()
        except ContainerNameError as e:
            self.error = str(e)

    def _build_session(
        self,
        retries_total: int,
        backoff: float,
        statuses: List[int],
        pool_connections: int,
        pool_maxsize: int,
        pool_block: bool,
    ) -> Session:
        sess = requests.Session()
        retry = Retry(
            total=retries_total,
            read=retries_total,
            connect=retries_total,
            status=retries_total,
            backoff_factor=backoff,
            status_forcelist=statuses,
            allowed_methods=frozenset(["POST"]),
            raise_on_status=False,
            respect_retry_after_header=True,
            backoff_max=30,  # Max 30 seconds between retries
            raise_on_redirect=False,
        )
        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            pool_block=pool_block,
        )
        sess.mount("https://", adapter)
        sess.mount("http://", adapter)
        return sess

    def _get_container_name(self) -> str:
        container_name = os.environ.get(self.env_var_name)
        if not container_name:
            raise ContainerNameError(f"{self.env_var_name} environment variable is not set or empty")
        return container_name

    def _make_idempotency_key(self, payload: Dict[str, Any]) -> str:
        stable = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return str(uuid.uuid5(self.idempotency_namespace, stable))

    def set_extra_headers(self, headers: Dict[str, str]) -> None:
        """Set extra headers to be included in the request.
        
        Note: This method is maintained for backward compatibility.
        Headers will be merged with the default Authorization header.
        """
        if not hasattr(self, '_extra_headers'):
            self._extra_headers = {}
        self._extra_headers.update(headers)

    def get_credentials(self, cred_list: List[str]) -> Dict[str, Any]:
        # Preserve original error shape
        if self.error:
            return {"error": {"code": 400, "message": self.error}}

        try:
            payload = {"credentials": cred_list, "container_name": self.container_name}
            headers = {"Authorization": f"Bearer {self.auth_token}"}

            # Merge extra headers for backward compatibility
            if hasattr(self, '_extra_headers'):
                headers.update(self._extra_headers)

            if self.use_idempotency_key:
                headers["Idempotency-Key"] = self._make_idempotency_key(payload)

            # Optional throttling
            if self._bucket:
                self._bucket.acquire()

            # Optional local concurrency cap
            acquire = getattr(self._sema, "acquire", None)
            release = getattr(self._sema, "release", None)
            if acquire:
                acquire()

            try:
                resp = self.session.post(
                    self.vault_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                
                # Let retries happen automatically, then handle final response
                if resp.status_code >= 400:
                    # After all retries are exhausted, return error in legacy format
                    try:
                        error_data = resp.json() if resp.text else {}
                    except json.JSONDecodeError:
                        error_data = {}
                    
                    return {
                        "error": {
                            "code": resp.status_code,
                            "message": error_data.get("message", f"HTTP {resp.status_code} error"),
                            "details": error_data
                        }
                    }

                if not resp.text:
                    return {"error": {"code": 204, "message": "Empty response from server"}}

                try:
                    return resp.json()
                except json.JSONDecodeError:
                    return {
                        "error": {"code": 500, "message": "Failed to decode JSON response"},
                        "details": {"status_code": resp.status_code, "content_type": resp.headers.get("Content-Type")},
                    }
                    
            finally:
                if release:
                    release()

        except requests.exceptions.Timeout as e:
            return {"error": {"code": 504, "message": f"Timed out contacting vault service: {str(e)}"}}
        except requests.exceptions.RequestException as e:
            return {"error": {"code": 500, "message": f"Failed to retrieve credentials: {str(e)}"}}


class _TokenBucket:
    """Simple token bucket used by the client for rate limiting."""
    def __init__(self, rate_per_sec: float, burst: int):
        self.rate = float(rate_per_sec)
        self.capacity = int(max(1, burst))
        self._tokens = float(self.capacity)
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                elapsed = now - self._last
                self._last = now
                self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                need = 1.0 - self._tokens
                wait_s = need / self.rate if self.rate > 0 else 0.01
            time.sleep(wait_s + random.uniform(0, 0.02))
