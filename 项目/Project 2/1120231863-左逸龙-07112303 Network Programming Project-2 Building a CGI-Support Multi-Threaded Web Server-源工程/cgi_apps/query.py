"""Student query CGI application."""

from __future__ import annotations

from contextlib import closing
from html import escape
from pathlib import Path
import sqlite3

from .common import CgiResult, html_document, parse_form, run_main


def run(environ: dict[str, str], body: bytes) -> CgiResult:
    try:
        values = parse_form(environ, body)
        student_id = values.get("student_id", "").strip()
        if not student_id or len(student_id) > 32:
            raise ValueError("请输入有效的学号")
        database_path = Path(environ["DATABASE_PATH"]).resolve()
        database_uri = f"{database_path.as_uri()}?mode=ro"
        with closing(sqlite3.connect(database_uri, uri=True)) as connection:
            row = connection.execute(
                "SELECT student_id, name, class_id "
                "FROM students WHERE student_id = ?",
                (student_id,),
            ).fetchone()
    except (KeyError, OSError, sqlite3.Error) as exc:
        return CgiResult(
            500,
            {"Content-Type": "text/html; charset=utf-8"},
            html_document("查询失败", f"<h1>查询失败</h1><p>{escape(str(exc))}</p>"),
        )
    except ValueError as exc:
        return CgiResult(
            400,
            {"Content-Type": "text/html; charset=utf-8"},
            html_document("请求错误", f"<h1>请求错误</h1><p>{escape(str(exc))}</p>"),
        )

    if row is None:
        content = f"<h1>学生信息查询</h1><p>未找到学号 {escape(student_id)} 对应的记录。</p>"
    else:
        content = (
            "<h1>学生信息查询结果</h1><table>"
            f"<tr><th>学号</th><td>{escape(row[0])}</td></tr>"
            f"<tr><th>姓名</th><td>{escape(row[1])}</td></tr>"
            f"<tr><th>班级</th><td>{escape(row[2])}</td></tr></table>"
        )
    return CgiResult(
        200,
        {"Content-Type": "text/html; charset=utf-8"},
        html_document("学生信息查询", content),
    )


def main() -> int:
    return run_main(run)


if __name__ == "__main__":
    raise SystemExit(main())
