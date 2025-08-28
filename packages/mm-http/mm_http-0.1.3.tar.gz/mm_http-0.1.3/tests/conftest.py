import os

import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def proxy_http() -> str:
    proxy = os.getenv("PROXY_HTTP")
    if not proxy:
        raise ValueError("PROXY_HTTP environment variable must be set")
    return proxy


@pytest.fixture
def proxy_socks5() -> str:
    proxy = os.getenv("PROXY_SOCKS5")
    if not proxy:
        raise ValueError("PROXPROXY_SOCKS5Y_HTTP environment variable must be set")
    return proxy
