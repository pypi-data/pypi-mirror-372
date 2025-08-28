# mm-http

A simple and convenient HTTP client library for Python with both synchronous and asynchronous support.

## Features

- **Simple API** for one-off HTTP requests
- **Sync and Async** support with identical interfaces
- **JSON path navigation** with dot notation (`response.parse_json_body("user.profile.name")`)
- **Proxy support** (HTTP and SOCKS5)
- **Unified error handling**
- **Type-safe** with full type annotations
- **No sessions** - optimized for simple, stateless requests

## Quick Start

### Async Usage

```python
from mm_http import http_request

# Simple GET request
response = await http_request("https://api.github.com/users/octocat")
user_name = response.parse_json_body("name")  # Navigate JSON with dot notation

# POST with JSON data
response = await http_request(
    "https://httpbin.org/post",
    method="POST",
    json={"key": "value"},
    headers={"Authorization": "Bearer token"}
)

# With proxy
response = await http_request(
    "https://api.ipify.org?format=json",
    proxy="socks5://127.0.0.1:1080"
)
```

### Sync Usage

```python
from mm_http import http_request_sync

# Same API, but synchronous
response = http_request_sync("https://api.github.com/users/octocat")
user_name = response.parse_json_body("name")
```

## API Reference

### Functions

- `http_request(url, **kwargs)` - Async HTTP request
- `http_request_sync(url, **kwargs)` - Sync HTTP request

### Parameters

- `url: str` - Request URL
- `method: str = "GET"` - HTTP method
- `params: dict[str, Any] | None = None` - URL query parameters
- `data: dict[str, object] | None = None` - Form data
- `json: dict[str, object] | None = None` - JSON data
- `headers: dict[str, str] | None = None` - HTTP headers
- `cookies: LooseCookies | None = None` - Cookies
- `user_agent: str | None = None` - User-Agent header
- `proxy: str | None = None` - Proxy URL (supports http://, https://, socks4://, socks5://)
- `timeout: float | None = 10.0` - Request timeout in seconds

### HttpResponse

```python
@dataclass
class HttpResponse:
    status_code: int | None
    error: HttpError | None
    error_message: str | None
    body: str | None
    headers: dict[str, str] | None

    def parse_json_body(self, path: str | None = None, none_on_error: bool = False) -> Any
    def is_err(self) -> bool
    def content_type(self) -> str | None
    def to_result_ok[T](self, value: T) -> Result[T]
    def to_result_err[T](self, error: str | Exception | None = None) -> Result[T]
```

### Error Types

```python
class HttpError(str, Enum):
    TIMEOUT = "timeout"
    PROXY = "proxy"
    INVALID_URL = "invalid_url"
    CONNECTION = "connection"
    ERROR = "error"
```

## Examples

### JSON Path Navigation

```python
response = await http_request("https://api.github.com/users/octocat")

# Instead of: json.loads(response.body)["plan"]["name"]
plan_name = response.parse_json_body("plan.name")

# Safe navigation - returns None if path doesn't exist
followers = response.parse_json_body("followers_count")
nonexistent = response.parse_json_body("does.not.exist")  # Returns None
```

### Error Handling

```python
response = await http_request("https://example.com", timeout=5.0)

if response.is_err():
    print(f"Request failed: {response.error} - {response.error_message}")
else:
    print(f"Success: {response.status_code}")
```

### Proxy Usage

```python
# HTTP proxy
response = await http_request(
    "https://httpbin.org/ip",
    proxy="http://proxy.example.com:8080"
)

# SOCKS5 proxy
response = await http_request(
    "https://httpbin.org/ip",
    proxy="socks5://127.0.0.1:1080"
)
```

### Custom Headers and User-Agent

```python
response = await http_request(
    "https://api.example.com/data",
    headers={
        "Authorization": "Bearer your-token",
        "Accept": "application/json"
    },
    user_agent="MyApp/1.0"
)
```

### Result Type Integration

For applications using `Result[T, E]` pattern, `HttpResponse` provides convenient methods to convert responses into Result types:

```python
from mm_result import Result

async def get_user_id() -> Result[int]:
    response = await http_request("https://api.example.com/user")

    if response.is_err():
        return response.to_result_err()  # Convert error to Result[T]

    user_id = response.parse_json_body("id")
    return response.to_result_ok(user_id)  # Convert success to Result[T]

# Usage
result = await get_user_id()
if result.is_ok():
    print(f"User ID: {result.value}")
else:
    print(f"Error: {result.error}")
    print(f"HTTP details: {result.extra}")  # Contains full HTTP response data
```

**Result Methods:**
- `to_result_ok(value)` - Create `Result[T]` with success value, preserving HTTP details in `extra`
- `to_result_err(error?)` - Create `Result[T]` with error, preserving HTTP details in `extra`

## When to Use

**Use mm-http when you need:**
- Simple, one-off HTTP requests
- JSON API interactions with easy data access
- Proxy support for requests
- Unified sync/async interface

**Use requests/aiohttp directly when you need:**
- Session management and connection pooling
- Complex authentication flows
- Streaming responses
- Advanced HTTP features
- Custom retry logic
