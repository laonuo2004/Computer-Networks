"""Route HTTP requests to static resources or CGI programs."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Protocol
from urllib.parse import unquote, urlsplit

from .http import HttpRequest, HttpResponse


class CgiHandler(Protocol):
    def execute(
        self,
        request: HttpRequest,
        client_address: tuple[str, int],
        server_address: tuple[str, int],
    ) -> HttpResponse: ...


class WebApplication:
    def __init__(self, webroot: Path, cgi_executor: CgiHandler) -> None:
        self.webroot = Path(webroot).resolve()
        self.cgi_executor = cgi_executor

    def handle(
        self,
        request: HttpRequest,
        client_address: tuple[str, int],
        server_address: tuple[str, int],
    ) -> HttpResponse:
        if request.method not in {"GET", "POST", "HEAD"}:
            return self.error_response(400, "服务器只支持 GET、POST 和 HEAD。")
        try:
            path = unquote(urlsplit(request.target).path, encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, ValueError):
            return self.error_response(400, "请求路径编码无效。")
        if "\x00" in path:
            return self.error_response(400, "请求路径包含非法字符。")

        components = [component.lower() for component in path.replace("\\", "/").split("/") if component]
        if components and components[0] in {"data", "log"}:
            return self.error_response(403, "该目录不能通过 HTTP 直接访问。")
        if components and components[0] == "cgi-bin":
            return self.cgi_executor.execute(request, client_address, server_address)
        if request.method == "POST":
            return self.error_response(400, "POST 只能提交到 CGI 程序。")

        relative_path = "index.html" if path == "/" else path.lstrip("/")
        candidate = (self.webroot / relative_path).resolve()
        if not candidate.is_relative_to(self.webroot):
            return self.error_response(403, "请求路径超出了 Web 根目录。")
        if candidate.is_dir():
            return self.error_response(403, "服务器不提供目录列表。")
        if not candidate.is_file():
            return self.error_response(404, "请求的资源不存在。")
        try:
            body = candidate.read_bytes()
        except OSError:
            return self.error_response(403, "服务器无法读取该资源。")
        content_type, _ = mimetypes.guess_type(candidate.name)
        content_type = content_type or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
            content_type += "; charset=utf-8"
        return HttpResponse(200, {"Content-Type": content_type}, body)

    def error_response(self, status: int, message: str) -> HttpResponse:
        page = self.webroot / f"{status}.html"
        try:
            body = page.read_bytes() if page.is_file() else b""
        except OSError:
            body = b""
        if not body:
            body = (
                "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>"
                f"<title>{status}</title></head><body><h1>{status}</h1><p>{message}</p></body></html>"
            ).encode("utf-8")
        return HttpResponse(status, {"Content-Type": "text/html; charset=utf-8"}, body)
