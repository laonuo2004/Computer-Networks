from __future__ import annotations

import threading
import time
import unittest

from server import connections


class FakeSocket:
    def __init__(self) -> None:
        self.shutdown_calls = 0
        self.close_calls = 0

    def shutdown(self, how: int) -> None:
        self.shutdown_calls += 1

    def close(self) -> None:
        self.close_calls += 1


class ConnectionManagerTests(unittest.TestCase):
    def make_manager(self, maximum: int):
        manager_type = getattr(connections, "ConnectionManager", None)
        self.assertIsNotNone(manager_type)
        return manager_type(maximum)

    def test_third_connection_evicts_oldest_when_limit_is_two(self) -> None:
        manager = self.make_manager(2)
        first_socket = FakeSocket()
        second_socket = FakeSocket()
        third_socket = FakeSocket()
        first = manager.admit(first_socket, ("127.0.0.1", 1001))
        manager.admit(second_socket, ("127.0.0.1", 1002))
        manager.admit(third_socket, ("127.0.0.1", 1003))
        self.assertTrue(first.closed.is_set())
        self.assertEqual(1, first_socket.shutdown_calls)
        self.assertEqual(1, first_socket.close_calls)
        self.assertEqual(2, manager.count)

    def test_evicted_queued_connection_is_never_acquired(self) -> None:
        manager = self.make_manager(2)
        first = manager.admit(FakeSocket(), ("127.0.0.1", 1001))
        second = manager.admit(FakeSocket(), ("127.0.0.1", 1002))
        third = manager.admit(FakeSocket(), ("127.0.0.1", 1003))
        acquired = [manager.acquire(), manager.acquire()]
        self.assertNotIn(first, acquired)
        self.assertEqual([second, third], acquired)

    def test_active_oldest_connection_is_closed(self) -> None:
        manager = self.make_manager(2)
        first_socket = FakeSocket()
        first = manager.admit(first_socket, ("127.0.0.1", 1001))
        self.assertIs(first, manager.acquire())
        second = manager.admit(FakeSocket(), ("127.0.0.1", 1002))
        third = manager.admit(FakeSocket(), ("127.0.0.1", 1003))
        self.assertTrue(first.closed.is_set())
        self.assertEqual([second, third], [manager.acquire(), manager.acquire()])

    def test_release_is_idempotent(self) -> None:
        manager = self.make_manager(1)
        sock = FakeSocket()
        context = manager.admit(sock, ("127.0.0.1", 1001))
        manager.acquire()
        manager.release(context)
        manager.release(context)
        self.assertEqual(0, manager.count)
        self.assertEqual(1, sock.close_calls)

    def test_close_wakes_waiting_acquire(self) -> None:
        manager = self.make_manager(1)
        result: list[object] = []

        def wait_for_connection() -> None:
            result.append(manager.acquire())

        thread = threading.Thread(target=wait_for_connection)
        thread.start()
        time.sleep(0.05)
        manager.close()
        thread.join(timeout=1)
        self.assertFalse(thread.is_alive())
        self.assertEqual([None], result)

    def test_rejects_invalid_limit(self) -> None:
        manager_type = getattr(connections, "ConnectionManager", None)
        self.assertIsNotNone(manager_type)
        with self.assertRaises(ValueError):
            manager_type(0)


if __name__ == "__main__":
    unittest.main()
