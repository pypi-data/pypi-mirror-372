import json
import time
from urllib.parse import urlencode, urlparse

from pytest_httpserver import HTTPServer
from werkzeug import Request, Response

from mm_http import HttpError, http_request_sync


def test_json_path(httpserver: HTTPServer):
    httpserver.expect_request("/test").respond_with_json({"a": {"b": {"c": 123}}})
    res = http_request_sync(httpserver.url_for("/test"))
    assert res.parse_json_body("a.b.c") == 123


def test_body_as_json_path_not_exists(httpserver: HTTPServer):
    httpserver.expect_request("/test").respond_with_json({"d": 1})
    res = http_request_sync(httpserver.url_for("/test"))
    assert res.parse_json_body("a.b.c") is None


def test_body_as_json_no_body(httpserver: HTTPServer):
    def handler(_request: Request) -> Response:
        raise RuntimeError

    httpserver.expect_request("/test").respond_with_handler(handler)
    res = http_request_sync(httpserver.url_for("/test"))
    assert res.parse_json_body("a.b.c", none_on_error=True) is None


def test_custom_user_agent(httpserver: HTTPServer):
    def handler(request: Request) -> Response:
        return Response(json.dumps({"user-agent": request.headers["user-agent"]}), content_type="application/json")

    httpserver.expect_request("/test").respond_with_handler(handler)
    user_agent = "moon cat"
    res = http_request_sync(httpserver.url_for("/test"), user_agent=user_agent)
    assert res.parse_json_body()["user-agent"] == user_agent


def test_params(httpserver: HTTPServer):
    data = {"a": 123, "b": "bla bla"}
    httpserver.expect_request("/test", query_string="a=123&b=bla+bla").respond_with_json(data)
    res = http_request_sync(httpserver.url_for("/test"), params=data)
    assert res.parse_json_body() == data


def test_post_with_params(httpserver: HTTPServer):
    data = {"a": 1}
    httpserver.expect_request("/test", query_string=urlencode(data)).respond_with_json(data)
    res = http_request_sync(httpserver.url_for("/test"), params=data)
    assert res.parse_json_body() == data


def test_timeout(httpserver: HTTPServer):
    def handler(_request: Request) -> Response:
        time.sleep(2)
        return Response("ok")

    httpserver.expect_request("/test").respond_with_handler(handler)
    res = http_request_sync(httpserver.url_for("/test"), timeout=1)
    assert res.error == "timeout"


def test_proxy_http(proxy_http: str):
    proxy = urlparse(proxy_http)
    res = http_request_sync("https://api.ipify.org?format=json", proxy=proxy_http, timeout=5)
    assert proxy.hostname in res.parse_json_body()["ip"]


def test_proxy_socks5(proxy_socks5: str):
    proxy = urlparse(proxy_socks5)
    res = http_request_sync("https://api.ipify.org?format=json", proxy=proxy_socks5, timeout=5)
    assert proxy.hostname in res.parse_json_body()["ip"]


def test_http_request_sync_invalid_url() -> None:
    """Test that http_request_sync returns INVALID_URL error for malformed URLs."""
    response = http_request_sync("not-a-valid-url")
    assert response.error == HttpError.INVALID_URL
    assert response.error_message is not None
    assert response.status_code is None
    assert response.body is None
    assert response.headers is None


def test_http_request_sync_invalid_url_with_proxy() -> None:
    """Test that http_request_sync returns INVALID_URL error for malformed URLs even with proxy."""
    response = http_request_sync("not-a-valid-url", proxy="http://proxy.example.com:8080")
    assert response.error == HttpError.INVALID_URL
    assert response.error_message is not None
    assert response.status_code is None
    assert response.body is None
    assert response.headers is None
