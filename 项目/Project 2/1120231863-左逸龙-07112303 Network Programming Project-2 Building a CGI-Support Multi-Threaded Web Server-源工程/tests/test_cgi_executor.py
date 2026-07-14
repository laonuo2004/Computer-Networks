from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from server import cgi_executor
from server.http import HttpRequest


class CgiExecutorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.webroot = self.root / "webroot"
        (self.webroot / "cgi-bin").mkdir(parents=True)

    def write_script(self, name: str, source: str) -> None:
        (self.webroot / "cgi-bin" / name).write_text(
            textwrap.dedent(source), encoding="utf-8"
        )

    def make_executor(self, mapping: dict[str, str], timeout: float = 1.0):
        executor_type = getattr(cgi_executor, "CgiExecutor", None)
        self.assertIsNotNone(executor_type)
        return executor_type(
            self.webroot,
            self.root,
            timeout=timeout,
            programs=mapping,
        )

    def test_passes_environment_and_post_body_to_real_process(self) -> None:
        self.write_script(
            "echo.py",
            """
            import os, sys
            length = int(os.environ['CONTENT_LENGTH'])
            body = sys.stdin.buffer.read(length)
            payload = '|'.join([
                os.environ['REQUEST_METHOD'],
                os.environ['SCRIPT_NAME'],
                os.environ['REMOTE_ADDR'],
                os.environ['HTTP_USER_AGENT'],
                body.decode(),
            ]).encode()
            sys.stdout.buffer.write(b'Content-Type: text/plain\\r\\n\\r\\n' + payload)
            """,
        )
        executor = self.make_executor({"/cgi-bin/echo.py": "echo"})
        body = b"value=42"
        request = HttpRequest(
            "POST",
            "/cgi-bin/echo.py",
            "HTTP/1.0",
            {
                "content-type": "application/x-www-form-urlencoded",
                "content-length": str(len(body)),
                "user-agent": "unit-test",
            },
            body,
        )
        response = executor.execute(
            request,
            client_address=("127.0.0.9", 51000),
            server_address=("127.0.0.1", 8888),
        )
        self.assertEqual(200, response.status)
        self.assertEqual("text/plain", response.headers["Content-Type"])
        self.assertEqual(
            b"POST|/cgi-bin/echo.py|127.0.0.9|unit-test|value=42",
            response.body,
        )

    def test_parses_status_header(self) -> None:
        self.write_script(
            "bad.py",
            """
            import sys
            sys.stdout.buffer.write(
                b'Status: 400 Bad Request\\r\\nContent-Type: text/plain\\r\\n\\r\\nbad input'
            )
            """,
        )
        executor = self.make_executor({"/cgi-bin/bad.py": "bad"})
        request = HttpRequest("GET", "/cgi-bin/bad.py", "HTTP/1.0", {}, b"")
        response = executor.execute(request, ("127.0.0.1", 1), ("127.0.0.1", 8888))
        self.assertEqual(400, response.status)
        self.assertEqual(b"bad input", response.body)

    def test_timeout_returns_500(self) -> None:
        self.write_script(
            "slow.py",
            """
            import time
            time.sleep(2)
            print('Content-Type: text/plain\\r\\n\\r\\nlate')
            """,
        )
        executor = self.make_executor({"/cgi-bin/slow.py": "slow"}, timeout=0.05)
        request = HttpRequest("GET", "/cgi-bin/slow.py", "HTTP/1.0", {}, b"")
        response = executor.execute(request, ("127.0.0.1", 1), ("127.0.0.1", 8888))
        self.assertEqual(500, response.status)
        self.assertIn("超时".encode("utf-8"), response.body)

    def test_malformed_output_returns_500(self) -> None:
        self.write_script("broken.py", "print('no cgi headers')")
        executor = self.make_executor({"/cgi-bin/broken.py": "broken"})
        request = HttpRequest("GET", "/cgi-bin/broken.py", "HTTP/1.0", {}, b"")
        response = executor.execute(request, ("127.0.0.1", 1), ("127.0.0.1", 8888))
        self.assertEqual(500, response.status)

    def test_unlisted_program_returns_403(self) -> None:
        executor = self.make_executor({})
        request = HttpRequest("GET", "/cgi-bin/other.py", "HTTP/1.0", {}, b"")
        response = executor.execute(request, ("127.0.0.1", 1), ("127.0.0.1", 8888))
        self.assertEqual(403, response.status)


if __name__ == "__main__":
    unittest.main()
