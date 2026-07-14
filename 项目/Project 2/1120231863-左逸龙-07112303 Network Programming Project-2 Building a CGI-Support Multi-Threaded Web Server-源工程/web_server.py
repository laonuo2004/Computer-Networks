"""Command-line entry point for the Project 2 web server."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Callable, Sequence

from server.core import ServerConfig, WebServer


def resource_base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Building a CGI-Support Multi-Threaded Web Server",
    )
    parser.add_argument("--host", default="127.0.0.1", help="listening address")
    parser.add_argument("--port", type=int, default=8888, help="listening TCP port")
    parser.add_argument("--workers", type=int, default=8, help="fixed worker thread count")
    parser.add_argument(
        "--max-connections",
        type=int,
        default=32,
        help="maximum open connections before the oldest is closed",
    )
    parser.add_argument(
        "--webroot",
        type=Path,
        default=resource_base() / "webroot",
        help="web server root directory",
    )
    parser.add_argument("--keep-alive-timeout", type=float, default=5.0)
    parser.add_argument("--cgi-timeout", type=float, default=5.0)
    parser.add_argument("--cgi-run", help=argparse.SUPPRESS)
    return parser


def resolve_cgi_runner(name: str) -> Callable[[], int]:
    if name == "calculator":
        from cgi_apps.calculator import main

        return main
    if name == "query":
        from cgi_apps.query import main

        return main
    raise ValueError(f"unknown CGI program: {name}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    if arguments.cgi_run:
        try:
            runner = resolve_cgi_runner(arguments.cgi_run)
        except ValueError as exc:
            parser.error(str(exc))
        return runner()

    try:
        config = ServerConfig(
            host=arguments.host,
            port=arguments.port,
            workers=arguments.workers,
            max_connections=arguments.max_connections,
            webroot=arguments.webroot,
            keep_alive_timeout=arguments.keep_alive_timeout,
            cgi_timeout=arguments.cgi_timeout,
        )
        server = WebServer(config)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print(
        f"Serving {config.webroot} at http://{config.host}:{config.port}/ "
        f"with {config.workers} workers (max connections: {config.max_connections})"
    )
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
