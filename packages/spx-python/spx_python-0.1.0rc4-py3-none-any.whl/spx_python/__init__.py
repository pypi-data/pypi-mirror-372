# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Hammerheads Engineers sp. z o.o.
# Author: Aleksander Stanik
import os
from spx_python.client import SpxClient

__version__ = '0.1.0-rc.4'
__all__ = ['init', 'SpxClient']


def init(
    product_key: str,
    address: str = "http://localhost:8000",
    transparent: bool = None,
    **kwargs
) -> SpxClient:
    """
    Initialize the SPX Python client against the SPX server.

    :param address: Base URL of the SPX server (including scheme and port).
    :param product_key: License or product key for authentication.
    :param kwargs: Additional options forwarded to SpxClient.
    :return: Configured SpxClient instance.
    """
    if transparent is None:
        env_transparent = os.getenv("SPX_TRANSPARENT", "").lower()
        if env_transparent in ("true", "1"):
            transparent = True
        elif env_transparent in ("false", "0"):
            transparent = False
        else:
            transparent = getattr(SpxClient, 'transparent_global_default', None)
    spx_client = SpxClient(base_url=address, product_key=product_key, transparent=transparent, **kwargs)
    return spx_client
