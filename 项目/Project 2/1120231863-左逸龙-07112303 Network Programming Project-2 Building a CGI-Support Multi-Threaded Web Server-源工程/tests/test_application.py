from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from server import application
from server.http import HttpRequest, HttpResponse


class RecordingCgiExecutor:
    def __init__(self) -> None:
        self.requests: list[HttpRequest] = []

    def execute(self, request, client_address, server_address) -> HttpResponse:
        self.requests.append(request)
        return HttpResponse(200, {"Content-Type": "text/plain"}, b"cgi")


class WebApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name) / "webroot"
        self.root.mkdir()
        (self.root / "index.html").write_text("home", encoding="utf-8")
        (self.root / "404.html").write_text("custom missing", encoding="utf-8")
        (self.root / "assets").mkdir()
        (self.root / "assets" / "style.css").write_text("body{}", encoding="utf-8")
        (self.root / "data").mkdir()
        (self.root / "data" / "secret.txt").write_text("secret", encoding="utf-8")
        self.cgi = RecordingCgiExecutor()

    def make_app(self):
        app_type = getattr(application, "WebApplication", None)
        self.assertIsNotNone(app_type)
        return app_type(self.root, self.cgi)

    @staticmethod
    def request(method: str, target: str) -> HttpRequest:
        return HttpRequest(method, target, "HTTP/1.0", {}, b"")

    def handle(self, method: str, target: str) -> HttpResponse:
        return self.make_app().handle(
            self.request(method, target),
            client_address=("127.0.0.1", 50000),
            server_address=("127.0.0.1", 8888),
        )

    def test_root_serves_index(self) -> None:
        response = self.handle("GET", "/")
        self.assertEqual(200, response.status)
        self.assertEqual(b"home", response.body)
        self.assertIn("text/html", response.headers["Content-Type"])

    def test_static_css_uses_css_mime_type(self) -> None:
        response = self.handle("GET", "/assets/style.css")
        self.assertEqual(200, response.status)
        self.assertIn("text/css", response.headers["Content-Type"])

    def test_missing_file_uses_custom_404_page(self) -> None:
        response = self.handle("GET", "/missing.html")
        self.assertEqual(404, response.status)
        self.assertEqual(b"custom missing", response.body)

    def test_percent_encoded_traversal_is_forbidden(self) -> None:
        response = self.handle("GET", "/%2e%2e/secret.txt")
        self.assertEqual(403, response.status)

    def test_data_directory_is_forbidden(self) -> None:
        response = self.handle("GET", "/data/secret.txt")
        self.assertEqual(403, response.status)

    def test_directory_listing_is_forbidden(self) -> None:
        response = self.handle("GET", "/assets/")
        self.assertEqual(403, response.status)

    def test_post_to_static_file_is_bad_request(self) -> None:
        response = self.handle("POST", "/index.html")
        self.assertEqual(400, response.status)

    def test_cgi_path_is_executed_not_served(self) -> None:
        response = self.handle("GET", "/cgi-bin/calculator.py")
        self.assertEqual(200, response.status)
        self.assertEqual(b"cgi", response.body)
        self.assertEqual(1, len(self.cgi.requests))


if __name__ == "__main__":
    unittest.main()
