"""Execute allow-listed CGI programs in child processes."""

from __future__ import annotations

from html import escape
import os
from pathlib import Path
import signal
import subprocess
import sys
from urllib.parse import urlsplit

from .http import HttpRequest, HttpResponse


DEFAULT_PROGRAMS = {
    "/cgi-bin/calculator.py": "calculator",
    "/cgi-bin/query.py": "query",
}

_HOP_BY_HOP = {"connection", "transfer-encoding", "content-length"}
_REASONS = {200: "OK", 400: "Bad Request", 403: "Forbidden", 404: "Not Found", 500: "Internal Server Error"}


class CgiExecutor:
    def __init__(
        self,
        webroot: Path,
        source_root: Path,
        *,
        timeout: float = 5.0,
        max_output_bytes: int = 1024 * 1024,
        programs: dict[str, str] | None = None,
        frozen: bool | None = None,
        executable: str | None = None,
    ) -> None:
        self.webroot = Path(webroot).resolve()
        self.source_root = Path(source_root).resolve()
        self.timeout = timeout
        self.max_output_bytes = max_output_bytes
        self.programs = DEFAULT_PROGRAMS.copy() if programs is None else dict(programs)
        self.frozen = bool(getattr(sys, "frozen", False)) if frozen is None else frozen
        self.executable = executable or sys.executable

    def execute(
        self,
        request: HttpRequest,
        client_address: tuple[str, int],
        server_address: tuple[str, int],
    ) -> HttpResponse:
        parsed_target = urlsplit(request.target)
        script_name = parsed_target.path
        program = self.programs.get(script_name)
        if program is None:
            return self._error(403, "该 CGI 程序未被服务器授权执行。")

        script_path = (self.webroot / script_name.lstrip("/")).resolve()
        if not self.frozen and not script_path.is_file():
            return self._error(404, "CGI 程序不存在。")

        environment = self._build_environment(
            request,
            script_name,
            parsed_target.query,
            client_address,
            server_address,
        )
        if self.frozen:
            command = [self.executable, "--cgi-run", program]
        else:
            command = [self.executable, str(script_path)]

        creation_flags = 0
        if os.name == "nt":
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.webroot,
                env=environment,
                shell=False,
                creationflags=creation_flags,
                start_new_session=os.name != "nt",
            )
        except OSError as exc:
            return self._error(500, f"无法启动 CGI 程序：{escape(str(exc))}")

        try:
            stdout, stderr = process.communicate(input=request.body, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            self._terminate_process_tree(process)
            try:
                process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
            return self._error(500, "CGI 程序执行超时。")

        if process.returncode != 0:
            return self._error(500, "CGI 程序异常退出。")
        if len(stdout) > self.max_output_bytes:
            return self._error(500, "CGI 程序输出超过服务器限制。")
        try:
            return self._parse_output(stdout)
        except ValueError:
            return self._error(500, "CGI 程序返回了无效响应。")

    @staticmethod
    def _terminate_process_tree(process: subprocess.Popen) -> None:
        if process.poll() is not None:
            return
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=2,
            )
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if process.poll() is None:
            process.kill()

    def _build_environment(
        self,
        request: HttpRequest,
        script_name: str,
        query_string: str,
        client_address: tuple[str, int],
        server_address: tuple[str, int],
    ) -> dict[str, str]:
        environment = os.environ.copy()
        environment.update(
            {
                "GATEWAY_INTERFACE": "CGI/1.1",
                "REQUEST_METHOD": request.method,
                "QUERY_STRING": query_string,
                "CONTENT_LENGTH": str(len(request.body)) if request.body else "",
                "CONTENT_TYPE": request.headers.get("content-type", ""),
                "SCRIPT_NAME": script_name,
                "SERVER_NAME": server_address[0],
                "SERVER_PORT": str(server_address[1]),
                "SERVER_PROTOCOL": request.version,
                "SERVER_SOFTWARE": "BIT-CGI-WebServer/1.0",
                "REMOTE_ADDR": client_address[0],
                "REMOTE_PORT": str(client_address[1]),
                "DOCUMENT_ROOT": str(self.webroot),
                "DATABASE_PATH": str(self.webroot / "data" / "students.db"),
            }
        )
        for name, value in request.headers.items():
            if name in {"content-length", "content-type", "connection", "authorization", "proxy-authorization"}:
                continue
            variable = "HTTP_" + name.upper().replace("-", "_")
            if variable == "HTTP_PROXY":
                continue
            environment[variable] = value
        python_path = environment.get("PYTHONPATH", "")
        environment["PYTHONPATH"] = str(self.source_root) + (os.pathsep + python_path if python_path else "")
        return environment

    @staticmethod
    def _parse_output(output: bytes) -> HttpResponse:
        if b"\r\n\r\n" in output:
            raw_headers, body = output.split(b"\r\n\r\n", 1)
            lines = raw_headers.split(b"\r\n")
        elif b"\n\n" in output:
            raw_headers, body = output.split(b"\n\n", 1)
            lines = raw_headers.split(b"\n")
        else:
            raise ValueError("missing CGI header separator")
        if len(raw_headers) > 64 * 1024:
            raise ValueError("CGI headers too large")

        status = 200
        headers: dict[str, str] = {}
        for raw_line in lines:
            try:
                line = raw_line.decode("iso-8859-1")
            except UnicodeDecodeError as exc:  # pragma: no cover
                raise ValueError("invalid CGI header encoding") from exc
            if ":" not in line:
                raise ValueError("malformed CGI header")
            name, value = line.split(":", 1)
            name = name.strip()
            value = value.strip()
            lower_name = name.lower()
            if lower_name == "status":
                code = value.split(None, 1)[0]
                if not code.isdecimal() or not 100 <= int(code) <= 599:
                    raise ValueError("invalid CGI status")
                status = int(code)
            elif lower_name not in _HOP_BY_HOP:
                canonical = "Content-Type" if lower_name == "content-type" else "-".join(part.capitalize() for part in lower_name.split("-"))
                headers[canonical] = value
        if "Content-Type" not in headers:
            raise ValueError("CGI response requires Content-Type")
        return HttpResponse(status, headers, body)

    @staticmethod
    def _error(status: int, message: str) -> HttpResponse:
        reason = _REASONS[status]
        body = (
            "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>"
            f"<title>{status} {reason}</title></head><body><h1>{status} {reason}</h1>"
            f"<p>{message}</p></body></html>"
        ).encode("utf-8")
        return HttpResponse(status, {"Content-Type": "text/html; charset=utf-8"}, body)
