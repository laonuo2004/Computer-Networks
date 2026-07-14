from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import http.client
import socket
import tempfile
import threading
import time
import unittest
from pathlib import Path

from server import core


class RunningServer:
    def __init__(self, webroot: Path, *, workers: int = 4, max_connections: int = 32, timeout: float = 1.0) -> None:
        config_type = getattr(core, "ServerConfig", None)
        server_type = getattr(core, "WebServer", None)
        if config_type is None or server_type is None:
            raise AssertionError("server core interfaces are missing")
        self.server = server_type(
            config_type(
                host="127.0.0.1",
                port=0,
                workers=workers,
                max_connections=max_connections,
                webroot=webroot,
                keep_alive_timeout=timeout,
                cgi_timeout=0.5,
            )
        )
        self.thread = threading.Thread(target=self.server.serve_forever, name="test-server")
        self.thread.start()
        if not self.server.ready.wait(2):
            raise AssertionError("server did not become ready")
        self.address = self.server.bound_address

    def close(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=3)
        if self.thread.is_alive():
            raise AssertionError("server thread did not stop")


class WebServerIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.webroot = Path(self.temp_dir.name) / "webroot"
        for directory in ("assets", "cgi-bin", "data", "log"):
            (self.webroot / directory).mkdir(parents=True, exist_ok=True)
        (self.webroot / "index.html").write_text("<h1>integration home</h1>", encoding="utf-8")
        (self.webroot / "assets" / "style.css").write_text("body{}", encoding="utf-8")
        for status in (400, 403, 404, 500):
            (self.webroot / f"{status}.html").write_text(f"error {status}", encoding="utf-8")
        (self.webroot / "data" / "students.csv").write_text(
            "student_id,name,class_id\n1120231863,左逸龙,07112303\n",
            encoding="utf-8",
        )
        (self.webroot / "cgi-bin" / "calculator.py").write_text(
            "from cgi_apps.calculator import main\nraise SystemExit(main())\n",
            encoding="utf-8",
        )
        (self.webroot / "cgi-bin" / "query.py").write_text(
            "from cgi_apps.query import main\nraise SystemExit(main())\n",
            encoding="utf-8",
        )
        self.running: RunningServer | None = None

    def tearDown(self) -> None:
        if self.running is not None:
            self.running.close()

    def start(self, **kwargs) -> RunningServer:
        self.running = RunningServer(self.webroot, **kwargs)
        return self.running

    def request(self, method: str, target: str, body: bytes | None = None, headers: dict[str, str] | None = None):
        running = self.running or self.start()
        connection = http.client.HTTPConnection(*running.address, timeout=3)
        connection.request(method, target, body=body, headers=headers or {})
        response = connection.getresponse()
        payload = response.read()
        result = response.status, dict(response.getheaders()), payload
        connection.close()
        return result

    def test_get_head_and_static_asset(self) -> None:
        self.start()
        status, headers, body = self.request("GET", "/")
        self.assertEqual(200, status)
        self.assertIn(b"integration home", body)
        head_status, head_headers, head_body = self.request("HEAD", "/index.html")
        self.assertEqual(200, head_status)
        self.assertEqual(b"", head_body)
        self.assertEqual(str(len(body)), head_headers["Content-Length"])
        css_status, css_headers, _ = self.request("GET", "/assets/style.css")
        self.assertEqual(200, css_status)
        self.assertIn("text/css", css_headers["Content-Type"])

    def test_calculator_and_query_run_as_cgi_processes(self) -> None:
        self.start()
        calculator_body = b"a=6&b=7&op=mul"
        status, _, body = self.request(
            "POST",
            "/cgi-bin/calculator.py",
            calculator_body,
            {"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(200, status)
        self.assertIn(b"42", body)
        query_body = b"student_id=1120231863"
        status, _, body = self.request(
            "POST",
            "/cgi-bin/query.py",
            query_body,
            {"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(200, status)
        self.assertIn("左逸龙".encode("utf-8"), body)

    def test_required_error_statuses_and_cgi_failure(self) -> None:
        self.start()
        self.assertEqual(404, self.request("GET", "/missing.html")[0])
        self.assertEqual(403, self.request("GET", "/%2e%2e/secret.txt")[0])
        self.assertEqual(400, self.request("PUT", "/index.html")[0])
        (self.webroot / "cgi-bin" / "calculator.py").write_text("print('broken')\n", encoding="utf-8")
        self.assertEqual(500, self.request("GET", "/cgi-bin/calculator.py")[0])

    def test_malformed_request_receives_400(self) -> None:
        running = self.start()
        with socket.create_connection(running.address, timeout=2) as client:
            client.sendall(b"GET /\r\n\r\n")
            data = self.recv_until_close(client)
        self.assertTrue(data.startswith(b"HTTP/1.0 400 Bad Request"))
        self.assertIn(b"error 400", data)

    def test_two_requests_share_http11_connection(self) -> None:
        running = self.start()
        with socket.create_connection(running.address, timeout=2) as client:
            client.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
            status1, headers1, body1, remainder = self.read_one_response(client)
            self.assertEqual(200, status1)
            self.assertEqual("keep-alive", headers1["connection"])
            self.assertIn(b"integration home", body1)
            client.sendall(
                b"GET /assets/style.css HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
            )
            status2, headers2, body2, _ = self.read_one_response(client, remainder)
            self.assertEqual(200, status2)
            self.assertEqual("close", headers2["connection"])
            self.assertEqual(b"body{}", body2)

    def test_forty_concurrent_requests_are_correct(self) -> None:
        self.start(workers=4, max_connections=64)

        def fetch(_: int) -> tuple[int, bytes]:
            status, _, body = self.request("GET", "/index.html")
            return status, body

        with ThreadPoolExecutor(max_workers=40) as pool:
            results = list(pool.map(fetch, range(40)))
        self.assertTrue(all(status == 200 for status, _ in results))
        self.assertTrue(all(body == b"<h1>integration home</h1>" for _, body in results))

    def test_new_connection_evicts_oldest_open_connection(self) -> None:
        running = self.start(workers=1, max_connections=2, timeout=2.0)
        first = socket.create_connection(running.address, timeout=2)
        second = socket.create_connection(running.address, timeout=2)
        self.addCleanup(first.close)
        self.addCleanup(second.close)
        first.sendall(b"GET / HTTP/1.1\r\nHost: first")
        self.wait_until(lambda: running.server.connection_count == 2)
        third = socket.create_connection(running.address, timeout=2)
        self.addCleanup(third.close)
        self.wait_until(lambda: running.server.connection_count == 2)
        first.settimeout(1)
        try:
            evicted_data = first.recv(1)
        except (ConnectionResetError, ConnectionAbortedError):
            evicted_data = b""
        self.assertEqual(b"", evicted_data)
        second.sendall(b"GET / HTTP/1.0\r\n\r\n")
        self.assertIn(b"HTTP/1.0 200 OK", self.recv_until_close(second))
        third.sendall(b"GET / HTTP/1.0\r\n\r\n")
        self.assertIn(b"HTTP/1.0 200 OK", self.recv_until_close(third))

    @staticmethod
    def recv_until_close(client: socket.socket) -> bytes:
        chunks: list[bytes] = []
        while True:
            chunk = client.recv(65536)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)

    @staticmethod
    def read_one_response(client: socket.socket, initial: bytes = b""):
        data = bytearray(initial)
        while b"\r\n\r\n" not in data:
            data.extend(client.recv(65536))
        raw_head, body = bytes(data).split(b"\r\n\r\n", 1)
        lines = raw_head.decode("iso-8859-1").split("\r\n")
        status = int(lines[0].split()[1])
        headers = {name.lower(): value.strip() for name, value in (line.split(":", 1) for line in lines[1:])}
        length = int(headers["content-length"])
        while len(body) < length:
            body += client.recv(65536)
        return status, headers, body[:length], body[length:]

    @staticmethod
    def wait_until(predicate, timeout: float = 2.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(0.01)
        raise AssertionError("condition was not met before timeout")


if __name__ == "__main__":
    unittest.main()
