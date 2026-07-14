from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import tempfile
import unittest
from pathlib import Path

from server import access_log
from server.http import HttpRequest


class AccessLoggerTests(unittest.TestCase):
    def test_concurrent_records_remain_one_complete_line_each(self) -> None:
        logger_type = getattr(access_log, "AccessLogger", None)
        self.assertIsNotNone(logger_type)
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = logger_type(Path(temp_dir))
            request = HttpRequest(
                "GET",
                "/index.html",
                "HTTP/1.0",
                {"referer": "http://example.test/", "user-agent": "unit-test"},
                b"",
            )
            with ThreadPoolExecutor(max_workers=8) as pool:
                list(
                    pool.map(
                        lambda index: logger.record(
                            (f"127.0.0.{index % 10}", 50000 + index),
                            request,
                            200,
                            123,
                        ),
                        range(50),
                    )
                )
            path = logger.path
            logger.close()
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(50, len(lines))
        self.assertTrue(all('"GET /index.html HTTP/1.0" 200 123' in line for line in lines))
        self.assertTrue(all('"http://example.test/" "unit-test"' in line for line in lines))


if __name__ == "__main__":
    unittest.main()
