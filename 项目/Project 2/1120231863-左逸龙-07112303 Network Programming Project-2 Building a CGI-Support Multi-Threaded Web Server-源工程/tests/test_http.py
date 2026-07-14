from __future__ import annotations

import unittest

from server import http


class FakeSocket:
    def __init__(self, chunks: list[bytes]) -> None:
        self.chunks = list(chunks)

    def recv(self, size: int) -> bytes:
        if not self.chunks:
            return b""
        chunk = self.chunks.pop(0)
        if len(chunk) <= size:
            return chunk
        self.chunks.insert(0, chunk[size:])
        return chunk[:size]


class HttpApiTests(unittest.TestCase):
    def test_exports_core_http_types(self) -> None:
        self.assertIsNotNone(getattr(http, "HttpRequest", None))
        self.assertIsNotNone(getattr(http, "HttpResponse", None))
        self.assertIsNotNone(getattr(http, "HttpConnectionReader", None))
        self.assertIsNotNone(getattr(http, "HttpRequestError", None))


class HttpConnectionReaderTests(unittest.TestCase):
    def make_reader(self, chunks: list[bytes], **kwargs: int):
        reader_type = getattr(http, "HttpConnectionReader", None)
        self.assertIsNotNone(reader_type)
        return reader_type(FakeSocket(chunks), **kwargs)

    def test_reads_fragmented_get_request(self) -> None:
        reader = self.make_reader(
            [b"GET /index", b".html HTTP/1.0\r\nUser-Agent: test", b"\r\n\r\n"]
        )
        request = reader.read_request()
        self.assertEqual("GET", request.method)
        self.assertEqual("/index.html", request.target)
        self.assertEqual("HTTP/1.0", request.version)
        self.assertEqual("test", request.headers["user-agent"])
        self.assertEqual(b"", request.body)

    def test_reads_post_body_by_content_length(self) -> None:
        reader = self.make_reader(
            [
                b"POST /cgi-bin/calculator.py HTTP/1.0\r\n",
                b"Content-Type: application/x-www-form-urlencoded\r\nContent-Length: 14\r\n\r\na=6&",
                b"b=7&op=mul",
            ]
        )
        request = reader.read_request()
        self.assertEqual(b"a=6&b=7&op=mul", request.body)

    def test_retains_pipelined_request_in_buffer(self) -> None:
        reader = self.make_reader(
            [
                b"GET /one HTTP/1.1\r\nHost: localhost\r\n\r\n"
                b"GET /two HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
            ]
        )
        first = reader.read_request()
        second = reader.read_request()
        self.assertEqual("/one", first.target)
        self.assertEqual("/two", second.target)

    def test_returns_none_on_clean_eof(self) -> None:
        reader = self.make_reader([])
        self.assertIsNone(reader.read_request())

    def test_rejects_post_without_content_length(self) -> None:
        reader = self.make_reader([b"POST /submit HTTP/1.0\r\n\r\n"])
        error_type = getattr(http, "HttpRequestError", Exception)
        with self.assertRaises(error_type):
            reader.read_request()

    def test_rejects_conflicting_content_lengths(self) -> None:
        reader = self.make_reader(
            [b"POST /submit HTTP/1.0\r\nContent-Length: 1\r\nContent-Length: 2\r\n\r\nx"]
        )
        error_type = getattr(http, "HttpRequestError", Exception)
        with self.assertRaises(error_type):
            reader.read_request()

    def test_rejects_transfer_encoding(self) -> None:
        reader = self.make_reader(
            [b"POST /submit HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\n"]
        )
        error_type = getattr(http, "HttpRequestError", Exception)
        with self.assertRaises(error_type):
            reader.read_request()

    def test_enforces_header_limit(self) -> None:
        reader = self.make_reader(
            [b"GET / HTTP/1.0\r\nX-Test: " + b"a" * 100 + b"\r\n\r\n"],
            max_header_bytes=32,
        )
        error_type = getattr(http, "HttpRequestError", Exception)
        with self.assertRaises(error_type):
            reader.read_request()


class HttpResponseTests(unittest.TestCase):
    def test_http10_closes_by_default(self) -> None:
        request_type = getattr(http, "HttpRequest", None)
        keep_alive = getattr(http, "should_keep_alive", None)
        self.assertIsNotNone(request_type)
        self.assertIsNotNone(keep_alive)
        request = request_type("GET", "/", "HTTP/1.0", {}, b"")
        self.assertFalse(keep_alive(request))

    def test_http11_keeps_alive_by_default(self) -> None:
        request_type = getattr(http, "HttpRequest", None)
        keep_alive = getattr(http, "should_keep_alive", None)
        self.assertIsNotNone(request_type)
        self.assertIsNotNone(keep_alive)
        request = request_type("GET", "/", "HTTP/1.1", {}, b"")
        self.assertTrue(keep_alive(request))

    def test_head_serialization_omits_body_but_keeps_length(self) -> None:
        request_type = getattr(http, "HttpRequest", None)
        response_type = getattr(http, "HttpResponse", None)
        serializer = getattr(http, "serialize_response", None)
        self.assertIsNotNone(request_type)
        self.assertIsNotNone(response_type)
        self.assertIsNotNone(serializer)
        request = request_type("HEAD", "/index.html", "HTTP/1.0", {}, b"")
        response = response_type(200, {"Content-Type": "text/plain"}, b"hello")
        wire = serializer(response, request, keep_alive=False)
        head, body = wire.split(b"\r\n\r\n", 1)
        self.assertIn(b"HTTP/1.0 200 OK", head)
        self.assertIn(b"Content-Length: 5", head)
        self.assertIn(b"Connection: close", head)
        self.assertEqual(b"", body)


if __name__ == "__main__":
    unittest.main()
