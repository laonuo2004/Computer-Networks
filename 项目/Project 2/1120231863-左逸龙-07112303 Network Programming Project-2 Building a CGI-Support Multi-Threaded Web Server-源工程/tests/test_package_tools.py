from __future__ import annotations

import unittest

from tools import package_smoke


class PackageSmokeToolTests(unittest.TestCase):
    def test_parse_http_response_returns_lowercase_headers(self) -> None:
        parser = getattr(package_smoke, "parse_http_response", None)
        self.assertIsNotNone(parser)
        status, headers, body = parser(
            b"HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 5\r\n\r\nhello"
        )
        self.assertEqual(200, status)
        self.assertEqual("text/plain", headers["content-type"])
        self.assertEqual(b"hello", body)

    def test_request_builder_sets_post_length(self) -> None:
        builder = getattr(package_smoke, "build_request", None)
        self.assertIsNotNone(builder)
        wire = builder("POST", "/cgi-bin/calculator.py", b"a=1&b=2&op=add")
        self.assertTrue(wire.startswith(b"POST /cgi-bin/calculator.py HTTP/1.0\r\n"))
        self.assertIn(b"Content-Length: 14\r\n", wire)
        self.assertTrue(wire.endswith(b"\r\n\r\na=1&b=2&op=add"))


if __name__ == "__main__":
    unittest.main()
