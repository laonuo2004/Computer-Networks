from __future__ import annotations

import csv
from pathlib import Path
import threading
import time


FIELDNAMES = [
    "timestamp",
    "host_id",
    "peer_id",
    "session_id",
    "direction",
    "event",
    "pdu_type",
    "seq",
    "ack",
    "status",
    "base",
    "next_seq",
    "expected_seq",
    "bytes",
    "note",
]


class CsvLogger:
    def __init__(self, path: Path, host_id: str, peer_id: str, session_id: int):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.host_id = host_id
        self.peer_id = peer_id
        self.session_id = session_id
        self._file = path.open("w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=FIELDNAMES)
        self._writer.writeheader()
        self._lock = threading.Lock()

    def log(self, **row: object) -> None:
        data = {name: "" for name in FIELDNAMES}
        data.update(
            timestamp=f"{time.time():.6f}",
            host_id=self.host_id,
            peer_id=self.peer_id,
            session_id=f"{self.session_id:08x}",
        )
        data.update({k: v for k, v in row.items() if k in data})
        with self._lock:
            self._writer.writerow(data)
            self._file.flush()

    def close(self) -> None:
        with self._lock:
            self._file.close()

