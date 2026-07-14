from __future__ import annotations

from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from cgi_apps import calculator, common, database, query


class CommonCgiTests(unittest.TestCase):
    def test_parse_post_form(self) -> None:
        parser = getattr(common, "parse_form", None)
        self.assertIsNotNone(parser)
        values = parser(
            {
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": "application/x-www-form-urlencoded",
                "CONTENT_LENGTH": "14",
            },
            b"a=6&b=7&op=mul",
        )
        self.assertEqual({"a": "6", "b": "7", "op": "mul"}, values)

    def test_parse_get_query_string(self) -> None:
        parser = getattr(common, "parse_form", None)
        self.assertIsNotNone(parser)
        values = parser(
            {"REQUEST_METHOD": "GET", "QUERY_STRING": "student_id=1120231863"},
            b"",
        )
        self.assertEqual("1120231863", values["student_id"])

    def test_cgi_wire_has_header_separator(self) -> None:
        result_type = getattr(common, "CgiResult", None)
        encoder = getattr(common, "encode_result", None)
        self.assertIsNotNone(result_type)
        self.assertIsNotNone(encoder)
        wire = encoder(result_type(400, {"Content-Type": "text/plain; charset=utf-8"}, b"bad"))
        self.assertTrue(wire.startswith(b"Status: 400 Bad Request\r\n"))
        self.assertIn(b"Content-Type: text/plain; charset=utf-8\r\n\r\nbad", wire)


class CalculatorCgiTests(unittest.TestCase):
    def test_four_arithmetic_operations(self) -> None:
        run = getattr(calculator, "run", None)
        self.assertIsNotNone(run)
        cases = {
            "add": "13",
            "sub": "-1",
            "mul": "42",
            "div": "0.8571428571",
        }
        for operation, expected in cases.items():
            with self.subTest(operation=operation):
                body = f"a=6&b=7&op={operation}".encode()
                result = run(
                    {
                        "REQUEST_METHOD": "POST",
                        "CONTENT_TYPE": "application/x-www-form-urlencoded",
                        "CONTENT_LENGTH": str(len(body)),
                    },
                    body,
                )
                self.assertEqual(200, result.status)
                self.assertIn(expected.encode(), result.body)

    def test_division_by_zero_returns_400(self) -> None:
        run = getattr(calculator, "run", None)
        self.assertIsNotNone(run)
        body = b"a=6&b=0&op=div"
        result = run(
            {
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": "application/x-www-form-urlencoded",
                "CONTENT_LENGTH": str(len(body)),
            },
            body,
        )
        self.assertEqual(400, result.status)
        self.assertIn("除数不能为 0".encode("utf-8"), result.body)

    def test_non_numeric_value_returns_400(self) -> None:
        run = getattr(calculator, "run", None)
        self.assertIsNotNone(run)
        body = b"a=<script>&b=7&op=add"
        result = run(
            {
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": "application/x-www-form-urlencoded",
                "CONTENT_LENGTH": str(len(body)),
            },
            body,
        )
        self.assertEqual(400, result.status)


class DatabaseAndQueryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        root = Path(self.temp_dir.name)
        self.csv_path = root / "students.csv"
        self.db_path = root / "students.db"
        self.csv_path.write_text(
            "student_id,name,class_id\n"
            "1120231863,左逸龙,07112303\n"
            "1120230001,测试同学,07112301\n",
            encoding="utf-8",
        )

    def test_database_is_created_from_csv(self) -> None:
        ensure = getattr(database, "ensure_database", None)
        self.assertIsNotNone(ensure)
        ensure(self.csv_path, self.db_path)
        with closing(sqlite3.connect(self.db_path)) as connection:
            row = connection.execute(
                "SELECT student_id, name, class_id FROM students WHERE student_id = ?",
                ("1120231863",),
            ).fetchone()
        self.assertEqual(("1120231863", "左逸龙", "07112303"), row)

    def test_query_returns_matching_student(self) -> None:
        ensure = getattr(database, "ensure_database", None)
        run = getattr(query, "run", None)
        self.assertIsNotNone(ensure)
        self.assertIsNotNone(run)
        ensure(self.csv_path, self.db_path)
        result = run(
            {"REQUEST_METHOD": "GET", "QUERY_STRING": "student_id=1120231863", "DATABASE_PATH": str(self.db_path)},
            b"",
        )
        self.assertEqual(200, result.status)
        self.assertIn("左逸龙".encode("utf-8"), result.body)
        self.assertIn(b"07112303", result.body)

    def test_query_injection_string_does_not_match(self) -> None:
        ensure = getattr(database, "ensure_database", None)
        run = getattr(query, "run", None)
        self.assertIsNotNone(ensure)
        self.assertIsNotNone(run)
        ensure(self.csv_path, self.db_path)
        result = run(
            {
                "REQUEST_METHOD": "GET",
                "QUERY_STRING": "student_id=%27+OR+1%3D1+--",
                "DATABASE_PATH": str(self.db_path),
            },
            b"",
        )
        self.assertEqual(200, result.status)
        self.assertIn("未找到".encode("utf-8"), result.body)
        self.assertNotIn("左逸龙".encode("utf-8"), result.body)


if __name__ == "__main__":
    unittest.main()
