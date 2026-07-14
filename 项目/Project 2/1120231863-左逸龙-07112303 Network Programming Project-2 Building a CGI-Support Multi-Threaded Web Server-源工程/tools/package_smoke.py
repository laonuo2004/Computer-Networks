"""Smoke-test a packaged Windows server outside the source tree."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
from typing import Sequence


def build_request(method: str, target: str, body: bytes = b"") -> bytes:
    lines = [
        f"{method} {target} HTTP/1.0",
        "Host: 127.0.0.1",
        "Connection: close",
    ]
    if body:
        lines.extend(
            [
                "Content-Type: application/x-www-form-urlencoded",
                f"Content-Length: {len(body)}",
            ]
        )
    return ("\r\n".join(lines) + "\r\n\r\n").encode("ascii") + body


def parse_http_response(wire: bytes) -> tuple[int, dict[str, str], bytes]:
    raw_headers, body = wire.split(b"\r\n\r\n", 1)
    lines = raw_headers.decode("iso-8859-1").split("\r\n")
    status = int(lines[0].split()[1])
    headers = {
        name.strip().lower(): value.strip()
        for name, value in (line.split(":", 1) for line in lines[1:])
    }
    return status, headers, body


def request(
    address: tuple[str, int],
    method: str,
    target: str,
    body: bytes = b"",
    timeout: float = 5.0,
) -> tuple[int, dict[str, str], bytes]:
    with socket.create_connection(address, timeout=timeout) as client:
        client.settimeout(timeout)
        client.sendall(build_request(method, target, body))
        chunks: list[bytes] = []
        while True:
            chunk = client.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
    return parse_http_response(b"".join(chunks))


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def wait_for_server(process: subprocess.Popen, address: tuple[str, int]) -> None:
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"packaged server exited with code {process.returncode}")
        try:
            with socket.create_connection(address, timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise TimeoutError("packaged server did not start")


def assert_package_behavior(executable: Path) -> None:
    package_directory = executable.parent
    port = find_free_port()
    address = ("127.0.0.1", port)
    process = subprocess.Popen(
        [
            str(executable),
            "--host", "127.0.0.1",
            "--port", str(port),
            "--workers", "4",
            "--max-connections", "64",
        ],
        cwd=package_directory,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_server(process, address)
        status, headers, home = request(address, "GET", "/")
        if status != 200 or "CGI 多线程 Web 服务器".encode("utf-8") not in home:
            raise AssertionError("packaged GET / failed")
        head_status, head_headers, head_body = request(address, "HEAD", "/index.html")
        if head_status != 200 or head_body or int(head_headers["content-length"]) != len(home):
            raise AssertionError("packaged HEAD failed")
        calculator = request(address, "POST", "/cgi-bin/calculator.py", b"a=6&b=7&op=mul")
        if calculator[0] != 200 or b"42" not in calculator[2]:
            raise AssertionError("packaged calculator CGI failed")
        query_result = request(address, "POST", "/cgi-bin/query.py", b"student_id=1120231863")
        if query_result[0] != 200 or "左逸龙".encode("utf-8") not in query_result[2]:
            raise AssertionError("packaged SQLite CGI failed")
        if request(address, "GET", "/%2e%2e/secret.txt")[0] != 403:
            raise AssertionError("packaged traversal protection failed")
        if request(address, "GET", "/missing.html")[0] != 404:
            raise AssertionError("packaged 404 failed")

        with ThreadPoolExecutor(max_workers=40) as pool:
            concurrent = list(pool.map(lambda _: request(address, "GET", "/index.html"), range(40)))
        if not all(result[0] == 200 and result[2] == home for result in concurrent):
            raise AssertionError("packaged concurrent requests failed")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

    if not (package_directory / "webroot" / "data" / "students.db").is_file():
        raise AssertionError("packaged server did not create students.db")
    logs = list((package_directory / "webroot" / "log").glob("access-*.log"))
    if not logs or not any(log.stat().st_size > 0 for log in logs):
        raise AssertionError("packaged server did not write access logs")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    executable = build_parser().parse_args(argv).executable.resolve()
    if not executable.is_file():
        raise SystemExit(f"executable not found: {executable}")
    with tempfile.TemporaryDirectory(prefix="project2-package-smoke-") as temp_dir:
        copied_directory = Path(temp_dir) / executable.parent.name
        shutil.copytree(executable.parent, copied_directory)
        copied_executable = copied_directory / executable.name
        assert_package_behavior(copied_executable)
        print(f"Package smoke test passed in isolated directory: {copied_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
