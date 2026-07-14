from __future__ import annotations

import unittest
from pathlib import Path

import web_server


class CommandLineTests(unittest.TestCase):
    def test_parser_defaults_match_assignment(self) -> None:
        builder = getattr(web_server, "build_parser", None)
        self.assertIsNotNone(builder)
        arguments = builder().parse_args([])
        self.assertEqual("127.0.0.1", arguments.host)
        self.assertEqual(8888, arguments.port)
        self.assertEqual(8, arguments.workers)
        self.assertEqual(32, arguments.max_connections)

    def test_cgi_runner_mapping_is_allow_listed(self) -> None:
        resolver = getattr(web_server, "resolve_cgi_runner", None)
        self.assertIsNotNone(resolver)
        self.assertTrue(callable(resolver("calculator")))
        self.assertTrue(callable(resolver("query")))
        with self.assertRaises(ValueError):
            resolver("other")


class ProjectAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.webroot = cls.root / "webroot"

    def test_required_webroot_files_exist(self) -> None:
        required = [
            "index.html",
            "calculator.html",
            "query.html",
            "400.html",
            "403.html",
            "404.html",
            "500.html",
            "assets/style.css",
            "assets/network.svg",
            "cgi-bin/calculator.py",
            "cgi-bin/query.py",
            "data/students.csv",
        ]
        missing = [name for name in required if not (self.webroot / name).is_file()]
        self.assertEqual([], missing)

    def test_forms_target_allow_listed_cgi_paths(self) -> None:
        calculator_path = self.webroot / "calculator.html"
        query_path = self.webroot / "query.html"
        self.assertTrue(calculator_path.is_file())
        self.assertTrue(query_path.is_file())
        calculator = calculator_path.read_text(encoding="utf-8")
        query = query_path.read_text(encoding="utf-8")
        self.assertIn('method="post"', calculator.lower())
        self.assertIn('action="/cgi-bin/calculator.py"', calculator)
        self.assertIn('method="post"', query.lower())
        self.assertIn('action="/cgi-bin/query.py"', query)

    def test_seed_contains_current_student(self) -> None:
        seed_path = self.webroot / "data" / "students.csv"
        self.assertTrue(seed_path.is_file())
        seed = seed_path.read_text(encoding="utf-8")
        self.assertIn("1120231863,左逸龙,07112303", seed)


if __name__ == "__main__":
    unittest.main()
