"""HTTP message parsing and serialization.

The project intentionally implements this layer directly over a TCP socket
instead of using :mod:`http.server`.  Only the HTTP/1.0 features required by
the assignment and a small HTTP/1.1 compatibility subset are supported.
"""

from __future__ import annotations

from dataclasses import dataclass
from email.utils import formatdate
from typing import Protocol


DEFAULT_MAX_HEADER_BYTES = 64 * 1024
DEFAULT_MAX_BODY_BYTES = 1024 * 1024


class Receivable(Protocol):
    def recv(self, size: int) -> bytes: ...


@dataclass(frozen=True, slots=True)
class HttpRequest:
    method: str
    target: str
    version: str
    headers: dict[str, str]
    body: bytes


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes


class HttpRequestError(ValueError):
    """A client request that can be answered with an HTTP error response."""

    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


class HttpConnectionReader:
    """Read one or more HTTP requests from a connected stream socket."""

    def __init__(
        self,
        sock: Receivable,
        *,
        max_header_bytes: int = DEFAULT_MAX_HEADER_BYTES,
        max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
        recv_size: int = 16 * 1024,
    ) -> None:
        self._socket = sock
        self._buffer = bytearray()
        self._max_header_bytes = max_header_bytes
        self._max_body_bytes = max_body_bytes
        self._recv_size = recv_size

    def read_request(self) -> HttpRequest | None:
        header_bytes = self._read_header_block()
        if header_bytes is None:
            return None

        try:
            header_text = header_bytes.decode("iso-8859-1")
        except UnicodeDecodeError as exc:  # pragma: no cover - all bytes map
            raise HttpRequestError("request headers are not ISO-8859-1") from exc

        lines = header_text.split("\r\n")
        request_line = lines[0].split()
        if len(request_line) != 3:
            raise HttpRequestError("malformed request line")
        method, target, version = request_line
        method = method.upper()
        if not target.startswith("/"):
            raise HttpRequestError("only origin-form request targets are supported")
        if version not in {"HTTP/1.0", "HTTP/1.1"}:
            raise HttpRequestError("unsupported HTTP version")

        headers, content_lengths = self._parse_headers(lines[1:])
        if "transfer-encoding" in headers:
            raise HttpRequestError("transfer encodings are not supported")
        if len(set(content_lengths)) > 1:
            raise HttpRequestError("conflicting Content-Length headers")
        if method == "POST" and not content_lengths:
            raise HttpRequestError("POST requires Content-Length")

        content_length = 0
        if content_lengths:
            raw_length = content_lengths[0]
            if not raw_length.isdecimal():
                raise HttpRequestError("invalid Content-Length")
            content_length = int(raw_length)
            if content_length > self._max_body_bytes:
                raise HttpRequestError("request body is too large")

        self._fill_buffer(content_length)
        body = bytes(self._buffer[:content_length])
        del self._buffer[:content_length]
        return HttpRequest(method, target, version, headers, body)

    def _read_header_block(self) -> bytes | None:
        delimiter = b"\r\n\r\n"
        while True:
            boundary = self._buffer.find(delimiter)
            if boundary >= 0:
                header_length = boundary + len(delimiter)
                if header_length > self._max_header_bytes:
                    raise HttpRequestError("request headers are too large")
                header = bytes(self._buffer[:boundary])
                del self._buffer[:header_length]
                return header
            if len(self._buffer) >= self._max_header_bytes:
                raise HttpRequestError("request headers are too large")
            chunk = self._socket.recv(self._recv_size)
            if not chunk:
                if not self._buffer:
                    return None
                raise HttpRequestError("connection closed before request headers completed")
            self._buffer.extend(chunk)

    @staticmethod
    def _parse_headers(lines: list[str]) -> tuple[dict[str, str], list[str]]:
        headers: dict[str, str] = {}
        content_lengths: list[str] = []
        for line in lines:
            if not line or line[0] in " \t" or ":" not in line:
                raise HttpRequestError("malformed request header")
            name, value = line.split(":", 1)
            name = name.strip().lower()
            value = value.strip()
            if not name:
                raise HttpRequestError("empty request header name")
            if name == "content-length":
                content_lengths.append(value)
            elif name in headers:
                headers[name] = f"{headers[name]}, {value}"
            else:
                headers[name] = value
        if content_lengths:
            headers["content-length"] = content_lengths[0]
        return headers, content_lengths

    def _fill_buffer(self, byte_count: int) -> None:
        while len(self._buffer) < byte_count:
            chunk = self._socket.recv(min(self._recv_size, byte_count - len(self._buffer)))
            if not chunk:
                raise HttpRequestError("connection closed before request body completed")
            self._buffer.extend(chunk)


def should_keep_alive(request: HttpRequest) -> bool:
    tokens = {
        token.strip().lower()
        for token in request.headers.get("connection", "").split(",")
        if token.strip()
    }
    if request.version == "HTTP/1.1":
        return "close" not in tokens
    return "keep-alive" in tokens


_REASONS = {
    200: "OK",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
}


def serialize_response(
    response: HttpResponse,
    request: HttpRequest,
    *,
    keep_alive: bool,
) -> bytes:
    """Serialize a response, suppressing the entity body for HEAD."""

    version = request.version if request.version in {"HTTP/1.0", "HTTP/1.1"} else "HTTP/1.0"
    reason = _REASONS.get(response.status, "Unknown")
    headers = {
        "Date": formatdate(usegmt=True),
        "Server": "BIT-CGI-WebServer/1.0",
        **response.headers,
        "Content-Length": str(len(response.body)),
        "Connection": "keep-alive" if keep_alive else "close",
    }
    lines = [f"{version} {response.status} {reason}"]
    for name, value in headers.items():
        if "\r" in name or "\n" in name or "\r" in value or "\n" in value:
            raise ValueError("response headers must not contain newlines")
        lines.append(f"{name}: {value}")
    head = ("\r\n".join(lines) + "\r\n\r\n").encode("iso-8859-1")
    return head if request.method == "HEAD" else head + response.body
