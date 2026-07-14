"""Shared CGI application helpers."""

from __future__ import annotations

from dataclasses import dataclass
import os
import sys
from urllib.parse import parse_qs


@dataclass(frozen=True, slots=True)
class CgiResult:
    status: int
    headers: dict[str, str]
    body: bytes


_REASONS = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    500: "Internal Server Error",
}


def parse_form(environ: dict[str, str], body: bytes) -> dict[str, str]:
    method = environ.get("REQUEST_METHOD", "GET").upper()
    if method == "POST":
        content_type = environ.get("CONTENT_TYPE", "").split(";", 1)[0].strip().lower()
        if content_type != "application/x-www-form-urlencoded":
            raise ValueError("仅支持 application/x-www-form-urlencoded 表单")
        raw_length = environ.get("CONTENT_LENGTH", "")
        if not raw_length.isdecimal() or int(raw_length) != len(body):
            raise ValueError("CONTENT_LENGTH 与表单正文不一致")
        encoded = body.decode("utf-8")
    elif method in {"GET", "HEAD"}:
        encoded = environ.get("QUERY_STRING", "")
    else:
        raise ValueError("不支持的 CGI 请求方法")

    parsed = parse_qs(encoded, keep_blank_values=True, strict_parsing=False)
    return {name: values[0] for name, values in parsed.items()}


def encode_result(result: CgiResult) -> bytes:
    reason = _REASONS.get(result.status, "Unknown")
    headers = dict(result.headers)
    headers.setdefault("Content-Type", "text/html; charset=utf-8")
    lines = [f"Status: {result.status} {reason}"]
    lines.extend(f"{name}: {value}" for name, value in headers.items())
    return ("\r\n".join(lines) + "\r\n\r\n").encode("iso-8859-1") + result.body


def html_document(title: str, content: str) -> bytes:
    return (
        "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>"
        f"<title>{title}</title><link rel='stylesheet' href='/assets/style.css'>"
        f"</head><body><main class='card'>{content}"
        "<p><a href='/'>返回首页</a></p></main></body></html>"
    ).encode("utf-8")


def run_main(run_function) -> int:
    raw_length = os.environ.get("CONTENT_LENGTH", "0")
    length = int(raw_length) if raw_length.isdecimal() else 0
    body = sys.stdin.buffer.read(length)
    result = run_function(dict(os.environ), body)
    sys.stdout.buffer.write(encode_result(result))
    sys.stdout.buffer.flush()
    return 0
