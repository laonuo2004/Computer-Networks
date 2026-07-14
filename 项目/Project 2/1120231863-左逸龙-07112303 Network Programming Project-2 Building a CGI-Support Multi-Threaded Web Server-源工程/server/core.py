"""Listener lifecycle and fixed worker pool."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import socket
import threading

from cgi_apps.database import ensure_database

from .access_log import AccessLogger
from .application import WebApplication
from .cgi_executor import CgiExecutor
from .connections import ConnectionContext, ConnectionManager
from .http import (
    DEFAULT_MAX_BODY_BYTES,
    DEFAULT_MAX_HEADER_BYTES,
    HttpConnectionReader,
    HttpRequest,
    HttpRequestError,
    serialize_response,
    should_keep_alive,
)


@dataclass(frozen=True, slots=True)
class ServerConfig:
    host: str
    port: int
    workers: int
    max_connections: int
    webroot: Path
    keep_alive_timeout: float = 5.0
    cgi_timeout: float = 5.0
    max_header_bytes: int = DEFAULT_MAX_HEADER_BYTES
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES
    max_requests_per_connection: int = 100

    def __post_init__(self) -> None:
        if not 0 <= self.port <= 65535:
            raise ValueError("port must be between 0 and 65535")
        if self.workers < 1:
            raise ValueError("workers must be at least 1")
        if self.max_connections < 1:
            raise ValueError("max_connections must be at least 1")
        if self.keep_alive_timeout <= 0 or self.cgi_timeout <= 0:
            raise ValueError("timeouts must be positive")
        if self.max_header_bytes < 1 or self.max_body_bytes < 0:
            raise ValueError("request limits are invalid")
        if self.max_requests_per_connection < 1:
            raise ValueError("max_requests_per_connection must be at least 1")


class WebServer:
    def __init__(self, config: ServerConfig) -> None:
        self.config = config
        self.webroot = Path(config.webroot).resolve()
        self.source_root = Path(__file__).resolve().parents[1]
        self.manager = ConnectionManager(config.max_connections)
        self.ready = threading.Event()
        self._stop = threading.Event()
        self._listener: socket.socket | None = None
        self._workers: list[threading.Thread] = []
        self._shutdown_lock = threading.Lock()
        self._finished = False
        self.bound_address: tuple[str, int] = (config.host, config.port)

        data_directory = self.webroot / "data"
        seed = data_directory / "students.csv"
        database = data_directory / "students.db"
        if seed.is_file():
            ensure_database(seed, database)
        self.logger = AccessLogger(self.webroot / "log")
        self.application = WebApplication(
            self.webroot,
            CgiExecutor(
                self.webroot,
                self.source_root,
                timeout=config.cgi_timeout,
            ),
        )

    @property
    def connection_count(self) -> int:
        return self.manager.count

    @property
    def worker_threads(self) -> tuple[threading.Thread, ...]:
        return tuple(self._workers)

    def serve_forever(self) -> None:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener = listener
        try:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((self.config.host, self.config.port))
            listener.listen(self.config.max_connections)
            listener.settimeout(0.25)
            host, port = listener.getsockname()[:2]
            self.bound_address = (str(host), int(port))
            self._start_workers()
            self.ready.set()

            while not self._stop.is_set():
                try:
                    client, address = listener.accept()
                except socket.timeout:
                    continue
                except OSError:
                    if self._stop.is_set():
                        break
                    raise
                client.settimeout(self.config.keep_alive_timeout)
                try:
                    self.manager.admit(client, (str(address[0]), int(address[1])))
                except RuntimeError:
                    client.close()
                    break
        finally:
            self.ready.set()
            self._finish()

    def shutdown(self) -> None:
        self._stop.set()
        listener = self._listener
        if listener is not None:
            try:
                listener.close()
            except OSError:
                pass
        self._finish()

    def _start_workers(self) -> None:
        for index in range(self.config.workers):
            thread = threading.Thread(
                target=self._worker_loop,
                name=f"web-worker-{index + 1}",
                daemon=False,
            )
            self._workers.append(thread)
            thread.start()

    def _worker_loop(self) -> None:
        while True:
            context = self.manager.acquire()
            if context is None:
                return
            try:
                self._handle_connection(context)
            finally:
                self.manager.release(context)

    def _handle_connection(self, context: ConnectionContext) -> None:
        client = context.socket
        reader = HttpConnectionReader(
            client,
            max_header_bytes=self.config.max_header_bytes,
            max_body_bytes=self.config.max_body_bytes,
        )
        for request_number in range(1, self.config.max_requests_per_connection + 1):
            request: HttpRequest | None = None
            try:
                request = reader.read_request()
            except HttpRequestError as exc:
                response = self.application.error_response(exc.status, exc.message)
                synthetic = HttpRequest("GET", "/", "HTTP/1.0", {}, b"")
                try:
                    client.sendall(serialize_response(response, synthetic, keep_alive=False))
                except OSError:
                    pass
                self.logger.record(context.address, None, response.status, len(response.body))
                return
            except (OSError, socket.timeout):
                return
            if request is None or context.closed.is_set():
                return

            keep_alive = (
                should_keep_alive(request)
                and request_number < self.config.max_requests_per_connection
                and not context.closed.is_set()
            )
            try:
                response = self.application.handle(
                    request,
                    context.address,
                    self.bound_address,
                )
            except Exception:
                response = self.application.error_response(500, "服务器处理请求时发生内部错误。")
                keep_alive = False

            try:
                client.sendall(
                    serialize_response(response, request, keep_alive=keep_alive)
                )
            except OSError:
                return
            finally:
                self.logger.record(
                    context.address,
                    request,
                    response.status,
                    len(response.body),
                )
            if not keep_alive:
                return

    def _finish(self) -> None:
        with self._shutdown_lock:
            if self._finished:
                return
            self._finished = True
            self._stop.set()
            self.manager.close()
            listener = self._listener
            if listener is not None:
                try:
                    listener.close()
                except OSError:
                    pass
            current = threading.current_thread()
            for thread in self._workers:
                if thread is not current:
                    thread.join(timeout=self.config.keep_alive_timeout + 1)
            self.logger.close()
