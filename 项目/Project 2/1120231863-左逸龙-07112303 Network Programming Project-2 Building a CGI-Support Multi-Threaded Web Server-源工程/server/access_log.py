"""Thread-safe access log writer."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import threading

from .http import HttpRequest


class AccessLogger:
    def __init__(self, log_directory: Path) -> None:
        directory = Path(log_directory)
        directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
        self.path = directory / f"access-{timestamp}.log"
        self._handle = self.path.open("a", encoding="utf-8", newline="\n")
        self._lock = threading.Lock()
        self._closed = False

    def record(
        self,
        client_address: tuple[str, int],
        request: HttpRequest | None,
        status: int,
        size: int,
    ) -> None:
        if request is None:
            request_line = "-"
            referer = "-"
            user_agent = "-"
        else:
            request_line = f"{request.method} {request.target} {request.version}"
            referer = request.headers.get("referer", "-")
            user_agent = request.headers.get("user-agent", "-")
        now = datetime.now().astimezone().strftime("%d/%b/%Y:%H:%M:%S %z")
        line = (
            f"{self._clean(client_address[0])} - - [{now}] "
            f'"{self._clean(request_line)}" {status} {size} '
            f'"{self._clean(referer)}" "{self._clean(user_agent)}"\n'
        )
        with self._lock:
            if self._closed:
                return
            self._handle.write(line)
            self._handle.flush()

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._handle.close()

    def __enter__(self) -> "AccessLogger":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    @staticmethod
    def _clean(value: str) -> str:
        return "".join(
            "_" if character in {'"', "\\", "\r", "\n"} else character
            for character in value
        )
