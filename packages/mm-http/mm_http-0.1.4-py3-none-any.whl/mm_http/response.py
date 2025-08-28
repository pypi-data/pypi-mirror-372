from __future__ import annotations

import enum
import json
from dataclasses import dataclass
from typing import Any

import pydash
from mm_result import Result


@enum.unique
class HttpError(str, enum.Enum):
    TIMEOUT = "timeout"
    PROXY = "proxy"
    INVALID_URL = "invalid_url"
    CONNECTION = "connection"
    ERROR = "error"


@dataclass
class HttpResponse:
    """HTTP response with status, error, body, and headers."""

    status_code: int | None = None
    error: HttpError | None = None
    error_message: str | None = None
    body: str | None = None
    headers: dict[str, str] | None = None

    def parse_json_body(self, path: str | None = None, none_on_error: bool = False) -> Any:  # noqa: ANN401
        """Parse JSON body and optionally extract value by path."""
        if self.body is None:
            if none_on_error:
                return None
            raise ValueError("Body is None")

        try:
            res = json.loads(self.body)
            return pydash.get(res, path, None) if path else res
        except json.JSONDecodeError:
            if none_on_error:
                return None
            raise

    def is_err(self) -> bool:
        """Check if response represents an error (has error or status >= 400)."""
        return self.error is not None or (self.status_code is not None and self.status_code >= 400)

    def to_result_err[T](self, error: str | Exception | tuple[str, Exception] | None = None) -> Result[T]:
        """Create error Result[T] from HttpResponse."""
        return Result.err(error or self.error or "error", extra=self.to_dict())

    def to_result_ok[T](self, value: T) -> Result[T]:
        """Create success Result[T] from HttpResponse with given value."""
        return Result.ok(value, extra=self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        """Convert HttpResponse to dictionary."""
        return {
            "status_code": self.status_code,
            "error": self.error.value if self.error else None,
            "error_message": self.error_message,
            "body": self.body,
            "headers": self.headers,
        }

    @property
    def content_type(self) -> str | None:
        """Get Content-Type header value (case-insensitive)."""
        if self.headers is None:
            return None
        for key in self.headers:
            if key.lower() == "content-type":
                return self.headers[key]
        return None

    def __repr__(self) -> str:
        parts: list[str] = []
        if self.status_code is not None:
            parts.append(f"status_code={self.status_code!r}")
        if self.error is not None:
            parts.append(f"error={self.error!r}")
        if self.error_message is not None:
            parts.append(f"error_message={self.error_message!r}")
        if self.body is not None:
            parts.append(f"body={self.body!r}")
        if self.headers is not None:
            parts.append(f"headers={self.headers!r}")
        return f"HttpResponse({', '.join(parts)})"
