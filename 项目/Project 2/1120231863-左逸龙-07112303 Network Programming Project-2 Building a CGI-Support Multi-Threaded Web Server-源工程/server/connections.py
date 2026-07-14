"""Connection admission and worker queue management."""

from __future__ import annotations

from collections import OrderedDict, deque
from dataclasses import dataclass, field
from itertools import count
import socket
import threading
import time
from typing import Protocol


class ClosableSocket(Protocol):
    def shutdown(self, how: int) -> None: ...
    def close(self) -> None: ...


@dataclass(eq=False, slots=True)
class ConnectionContext:
    connection_id: int
    socket: ClosableSocket
    address: tuple[str, int]
    accepted_at: float
    closed: threading.Event = field(default_factory=threading.Event)
    active: bool = False


class ConnectionManager:
    """Bound the open connections and feed them to a fixed worker pool.

    A single condition protects both the acceptance-order registry and the
    pending deque.  This makes it possible to remove an evicted queued
    connection before any worker can acquire it.
    """

    def __init__(self, max_connections: int) -> None:
        if max_connections < 1:
            raise ValueError("max_connections must be at least 1")
        self.max_connections = max_connections
        self._condition = threading.Condition(threading.RLock())
        self._connections: OrderedDict[int, ConnectionContext] = OrderedDict()
        self._pending: deque[ConnectionContext] = deque()
        self._ids = count(1)
        self._stopped = False

    @property
    def count(self) -> int:
        with self._condition:
            return len(self._connections)

    def admit(
        self,
        sock: ClosableSocket,
        address: tuple[str, int],
    ) -> ConnectionContext:
        evicted: ConnectionContext | None = None
        with self._condition:
            if self._stopped:
                raise RuntimeError("connection manager is closed")
            if len(self._connections) >= self.max_connections:
                _, evicted = self._connections.popitem(last=False)
                self._remove_pending(evicted.connection_id)
                evicted.closed.set()

            context = ConnectionContext(
                connection_id=next(self._ids),
                socket=sock,
                address=address,
                accepted_at=time.monotonic(),
            )
            self._connections[context.connection_id] = context
            self._pending.append(context)
            self._condition.notify()

        if evicted is not None:
            self._close_socket(evicted.socket)
        return context

    def acquire(self) -> ConnectionContext | None:
        with self._condition:
            while True:
                while not self._pending and not self._stopped:
                    self._condition.wait()
                if self._stopped:
                    return None
                context = self._pending.popleft()
                if context.closed.is_set():
                    continue
                if context.connection_id not in self._connections:
                    continue
                context.active = True
                return context

    def release(self, context: ConnectionContext) -> None:
        should_close = False
        with self._condition:
            registered = self._connections.pop(context.connection_id, None)
            if registered is not None:
                self._remove_pending(context.connection_id)
                context.closed.set()
                context.active = False
                should_close = True
        if should_close:
            self._close_socket(context.socket)

    def close(self) -> None:
        with self._condition:
            if self._stopped:
                return
            self._stopped = True
            contexts = list(self._connections.values())
            self._connections.clear()
            self._pending.clear()
            for context in contexts:
                context.closed.set()
                context.active = False
            self._condition.notify_all()
        for context in contexts:
            self._close_socket(context.socket)

    def _remove_pending(self, connection_id: int) -> None:
        self._pending = deque(
            context
            for context in self._pending
            if context.connection_id != connection_id
        )

    @staticmethod
    def _close_socket(sock: ClosableSocket) -> None:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        finally:
            try:
                sock.close()
            except OSError:
                pass
