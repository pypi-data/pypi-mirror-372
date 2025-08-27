# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Hammerheads Engineers sp. z o.o.
# Author: Aleksander Stanik
"""
SPX Python Client

Dictionary-like interface to SPX Server API v3.
Supports GET and PUT for components and attributes under a named system.
"""
import requests
import json
import os
import threading
import contextlib
from collections.abc import MutableMapping
from typing import Optional, List, Any

# ---------------------------------------------------------------------------
# Global / thread-local transparent mode controls
# ---------------------------------------------------------------------------
_GLOBAL_TRANSPARENT = False
_thread_local = threading.local()


def set_global_transparent(enabled: bool) -> None:
    """
    Set process-wide transparent mode for newly constructed SpxClient instances.
    Explicit SpxClient(transparent=...) always takes precedence.
    """
    global _GLOBAL_TRANSPARENT
    _GLOBAL_TRANSPARENT = bool(enabled)


def get_global_transparent() -> bool:
    """
    Return effective transparent mode from (in order of precedence):
      1) thread-local override set by `transparent_mode` context manager
      2) environment variable SPX_TRANSPARENT (1/true/yes/on)
      3) process-global flag set via set_global_transparent()
    """
    tl = getattr(_thread_local, "transparent", None)
    if tl is not None:
        return bool(tl)
    env = os.getenv("SPX_TRANSPARENT")
    if env is not None:
        return env.strip().lower() in {"1", "true", "yes", "on"}
    return _GLOBAL_TRANSPARENT


@contextlib.contextmanager
def transparent_mode(enabled: bool):
    """
    Temporarily set transparent mode for the current thread.
    Usage:
        with transparent_mode(True):
            # all new SpxClient() created here default to transparent=True
            ...
    """
    prev = getattr(_thread_local, "transparent", None)
    _thread_local.transparent = bool(enabled)
    try:
        yield
    finally:
        if prev is None:
            try:
                delattr(_thread_local, "transparent")
            except AttributeError:
                pass
        else:
            _thread_local.transparent = prev


class _TransparentSentinel:
    """
    No-op placeholder used when SpxClient runs in transparent mode.

    Behaves as:
    - callable: returns {"result": True}
    - attribute access: returns itself again (chaining-friendly)
    - setting attributes: ignored
    - numeric cast: 0 / 0.0
    - iteration: empty
    - truthiness: False
    """
    def __call__(self, *args, **kwargs):
        return {"result": True}

    def __getattr__(self, name: str):
        return self

    def __setattr__(self, name: str, value: Any):
        # ignore writes
        pass

    def __repr__(self):
        return "<transparent>"

    def __str__(self):
        return "<transparent>"

    def __bool__(self):
        return False

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __iter__(self):
        return iter(())


class SpxClient(MutableMapping):
    """
    A client for SPX Server API v3 with dict-like access.

    Usage:
        client = SpxClient(
            base_url='http://127.0.0.1:8000',
            product_key='YOUR_PRODUCT_KEY',
            system_name='your_system'
        )
        # Read an attribute:
        temp = client['timer'].time
        # Set an attribute:
        client['timer'].time = 5.0
        # Get full component or root JSON:
        data = client ['timer'] # returns JSON at current path

        # Transparent mode (process-wide / thread-local / env):
        #   set_global_transparent(True)
        #   with transparent_mode(True):
        #       ...
        #   export SPX_TRANSPARENT=1
        # Or per-instance:
        #   SpxClient(..., transparent=True)
    """
    def __init__(self,
                 base_url: str,
                 product_key: str,
                 http_client=None,
                 path: Optional[List[str]] = None,
                 transparent: Optional[bool] = None
                 ):
        self.base_url = base_url.rstrip('/')
        self.product_key = product_key
        self.path = path or []
        self.headers = {
            'Authorization': f'Bearer {self.product_key}',
            'Content-Type': 'application/json'
        }
        # allow injection of a custom HTTP client (e.g. FastAPI TestClient)
        self.http = http_client or requests
        # Determine effective transparent mode:
        # explicit arg > thread-local ctx > env var > module-global default
        effective_transparent = get_global_transparent() if transparent is None else bool(transparent)
        # set transparently via __dict__ to avoid __setattr__ side-effects during init
        self.__dict__["transparent"] = bool(effective_transparent)
        self.__dict__["_t"] = _TransparentSentinel() if self.__dict__["transparent"] else None

    def _build_url(self) -> str:
        if getattr(self, "transparent", False):
            # URL is irrelevant in transparent mode; return a stable pseudo-url
            return "transparent://"
        segments = [self.base_url, 'api', 'v3', 'system'] + self.path
        return '/'.join(segments)

    def __getitem__(self, key: str):
        if self.transparent:
            new_path = self.path + [key]
            return SpxClient(self.base_url, self.product_key, http_client=self.http, path=new_path, transparent=True)
        # Extend path and perform GET
        new_path = self.path + [key]
        url = '/'.join([self.base_url, 'api', 'v3', 'system'] + new_path)
        resp = self.http.get(url, headers=self.headers)
        resp.raise_for_status()
        data = resp.json()
        # Leaf attribute returns {'value': ...}
        if isinstance(data, dict) and 'value' in data:
            return data['value']
        # Otherwise return a new client focused on the deeper path
        return SpxClient(self.base_url,
                         self.product_key,
                         http_client=self.http,
                         path=new_path,
                         transparent=self.transparent)

    def __setitem__(self, key: str, value):
        if self.transparent:
            return {}
        # Extend path and perform PUT
        url = '/'.join([self.base_url, 'api', 'v3', 'system'] + self.path)
        payload = {key: value}
        resp = self.http.put(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        # Return JSON response or empty dict
        try:
            return resp.json()
        except ValueError:
            return {}

    def __delitem__(self, key: str):
        if self.transparent:
            return None
        # Extend path and perform DELETE
        new_path = self.path + [key]
        url = '/'.join([self.base_url, 'api', 'v3', 'system'] + new_path)
        resp = self.http.delete(url, headers=self.headers)
        resp.raise_for_status()
        return None

    def __contains__(self, key: str) -> bool:
        """
        Dictionary-like membership test at the current path.
        Returns True if `key` exists in the JSON data returned by GET.
        """
        if self.transparent:
            return False
        data = self.get()
        children = data.get('children', [])
        return any(child.get('name') == key for child in children)

    def get(self):
        """
        GET the full JSON at current path.
        """
        if self.transparent:
            return {}
        url = self._build_url()
        resp = self.http.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def to_dict(self) -> dict:
        """
        Return the current path's JSON as a pure Python dict.
        """
        return self.get()

    def __call__(self, *args, **kwargs):
        """Allow calling any SpxClient in transparent mode as a no-op.
        This keeps attribute-access chains usable for RPC-like calls
        (e.g., client.instances.sensor.reset()).
        """
        if getattr(self, "transparent", False):
            return {"result": True}
        raise TypeError(
            "SpxClient is not callable in non-transparent mode; "
            "use attribute access to obtain a method stub (e.g. client.reset(...))."
        )

    def __repr__(self):
        return f"<SpxClient path={'/'.join(self.path) or '<root>'}>"

    def __eq__(self, other):
        """
        Compare this client's data to another client or dict by comparing
        their JSON structures.
        """
        if isinstance(other, SpxClient):
            return self.to_dict() == other.to_dict()
        if isinstance(other, dict):
            return self.to_dict() == other
        return False

    def __ne__(self, other):
        """
        Inverse of __eq__ for inequality comparison.
        """
        return not (self == other)

    def __str__(self):
        """
        Return the full system structure from the current path
        as formatted JSON.
        """

        data = self.get()
        return json.dumps(data, indent=2)

    def _child_names(self, data: dict) -> list[str]:
        """Return child component names from a system JSON dict."""
        return [child.get('name') for child in data.get('children', []) if isinstance(child, dict) and 'name' in child]

    def _call_method(self, method_name, **kwargs):
        if self.transparent:
            return {"result": True}
        url = f"{self._build_url()}/method/{method_name}"
        resp = self.http.post(url, json=kwargs, headers=self.headers)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return None

    def __getattr__(self, key: str):
        # never intercept private/special names
        if key.startswith("_"):
            error_msg = (
                f"{type(self).__name__!r} has no attribute "
                f"{key!r}"
            )
            raise AttributeError(error_msg)
        # In transparent mode, attribute-style traversal should return a new
        # SpxClient focused on the extended path, without performing any HTTP.
        if getattr(self, "transparent", False):
            new_path = self.path + [key]
            return SpxClient(
                self.base_url,
                self.product_key,
                http_client=self.http,
                path=new_path,
                transparent=True,
            )
        data = object.__getattribute__(self, "get")()
        # top-level simple values
        if key in data and not isinstance(data[key], dict):
            return data[key]

        # attributes under 'attr'
        attr_sec = data.get("attr", {})
        if key in attr_sec:
            return attr_sec[key].get("value")

        # child components -> return a deeper SpxClient wrapper
        if any(child_name == key for child_name in self._child_names(data)):
            new_path = self.path + [key]
            return SpxClient(
                self.base_url,
                self.product_key,
                http_client=self.http,
                path=new_path,
                transparent=self.transparent,
            )

        # fallback: treat as RPC method
        return lambda **kwargs: self._call_method(key, **kwargs)

    def __setattr__(self, key: str, value):
        if key == "transparent":
            self.__dict__["transparent"] = bool(value)
            # keep sentinel in sync
            if self.__dict__["transparent"]:
                self.__dict__["_t"] = _TransparentSentinel()
            else:
                # remove sentinel when leaving transparent mode
                self.__dict__["_t"] = None
            return

        # Attributes that belong to the client object itself and must never trigger HTTP calls
        internal_keys = ('base_url', 'product_key', 'http', 'path', 'headers', '_t')

        # If we are setting any internal attribute, store it directly
        if key in internal_keys:
            super().__setattr__(key, value)
            return

        # In transparent mode, ignore any mutations to remote attributes
        try:
            is_transparent = object.__getattribute__(self, "transparent")
        except AttributeError:
            is_transparent = False

        if is_transparent:
            # no-op in transparent mode
            return {}

        # Otherwise, attempt to set attribute value via API under /attr/<key>
        new_path = self.path + ["attr", key]
        url = '/'.join([self.base_url, 'api', 'v3', 'system'] + new_path)
        payload = {'value': value}
        resp = self.http.put(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return {}

    def __iter__(self):
        """
        Iterate over keys in the current mapping:
        attribute names and child component names.
        """
        if self.transparent:
            return iter([])
        data = self.get()
        # Only child component names from 'children' list
        child_keys = [child.get('name') for child in data.get('children', [])]
        for key in child_keys:
            yield key

    def __len__(self):
        """
        Return the total number of keys in the mapping.
        """
        if self.transparent:
            return 0
        data = self.get()
        return len(data.get('attr', {})) + len(data.get('children', []))

    def keys(self):
        if self.transparent:
            return []
        return list(self.__iter__())

    def items(self):
        if self.transparent:
            return []
        return [(key, self[key]) for key in self]

    def values(self):
        if self.transparent:
            return []
        return [self[key] for key in self]
