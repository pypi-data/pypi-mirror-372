from typing import Any

import aiohttp
from aiohttp import ClientHttpProxyError, InvalidUrlClientError
from aiohttp.typedefs import LooseCookies
from aiohttp_socks import ProxyConnectionError, ProxyConnector
from multidict import CIMultiDictProxy

from .response import HttpError, HttpResponse


async def http_request(
    url: str,
    *,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    data: dict[str, object] | None = None,
    json: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    cookies: LooseCookies | None = None,
    user_agent: str | None = None,
    proxy: str | None = None,
    timeout: float | None = 10.0,
) -> HttpResponse:
    """
    Send an HTTP request and return the response.
    """
    timeout_ = aiohttp.ClientTimeout(total=timeout) if timeout else None
    if user_agent:
        if not headers:
            headers = {}
        headers["User-Agent"] = user_agent

    try:
        if proxy and proxy.startswith("socks"):
            return await _request_with_socks_proxy(
                url,
                method=method,
                params=params,
                data=data,
                json=json,
                headers=headers,
                cookies=cookies,
                proxy=proxy,
                timeout=timeout_,
            )
        return await _request_with_http_or_none_proxy(
            url,
            method=method,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            proxy=proxy,
            timeout=timeout_,
        )
    except TimeoutError as err:
        return HttpResponse(error=HttpError.TIMEOUT, error_message=str(err))
    except (aiohttp.ClientProxyConnectionError, ProxyConnectionError, ClientHttpProxyError) as err:
        return HttpResponse(error=HttpError.PROXY, error_message=str(err))
    except InvalidUrlClientError as e:
        return HttpResponse(error=HttpError.INVALID_URL, error_message=str(e))
    except Exception as err:
        return HttpResponse(error=HttpError.ERROR, error_message=str(err))


async def _request_with_http_or_none_proxy(
    url: str,
    *,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    data: dict[str, object] | None = None,
    json: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    cookies: LooseCookies | None = None,
    proxy: str | None = None,
    timeout: aiohttp.ClientTimeout | None,
) -> HttpResponse:
    async with aiohttp.request(
        method, url, params=params, data=data, json=json, headers=headers, cookies=cookies, proxy=proxy, timeout=timeout
    ) as res:
        return HttpResponse(
            status_code=res.status,
            error=None,
            error_message=None,
            body=(await res.read()).decode(),
            headers=headers_dict(res.headers),
        )


async def _request_with_socks_proxy(
    url: str,
    *,
    method: str = "GET",
    proxy: str,
    params: dict[str, Any] | None = None,
    data: dict[str, object] | None = None,
    json: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    cookies: LooseCookies | None = None,
    timeout: aiohttp.ClientTimeout | None,
) -> HttpResponse:
    connector = ProxyConnector.from_url(proxy)
    async with (
        aiohttp.ClientSession(connector=connector) as session,
        session.request(
            method, url, params=params, data=data, json=json, headers=headers, cookies=cookies, timeout=timeout
        ) as res,
    ):
        return HttpResponse(
            status_code=res.status,
            error=None,
            error_message=None,
            body=(await res.read()).decode(),
            headers=headers_dict(res.headers),
        )


def headers_dict(headers: CIMultiDictProxy[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key in headers:
        values = headers.getall(key)
        if len(values) == 1:
            result[key] = values[0]
        else:
            result[key] = ", ".join(values)
    return result
