"""SQLite database initialization helpers."""

from __future__ import annotations

import csv
from contextlib import closing
import os
from pathlib import Path
import sqlite3
import threading


def ensure_database(csv_path: Path, db_path: Path) -> Path:
    """Create the read-only query database from a human-readable CSV seed."""

    csv_path = Path(csv_path)
    db_path = Path(db_path)
    if db_path.is_file():
        return db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    required = {"student_id", "name", "class_id"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("students.csv must contain student_id,name,class_id")

    temporary = db_path.with_name(
        f".{db_path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
    )
    try:
        with closing(sqlite3.connect(temporary)) as connection:
            with connection:
                connection.execute(
                    "CREATE TABLE students ("
                    "student_id TEXT PRIMARY KEY, "
                    "name TEXT NOT NULL, "
                    "class_id TEXT NOT NULL)"
                )
                connection.executemany(
                    "INSERT INTO students(student_id, name, class_id) VALUES (?, ?, ?)",
                    [
                        (row["student_id"], row["name"], row["class_id"])
                        for row in rows
                    ],
                )
        os.replace(temporary, db_path)
    finally:
        temporary.unlink(missing_ok=True)
    return db_path
