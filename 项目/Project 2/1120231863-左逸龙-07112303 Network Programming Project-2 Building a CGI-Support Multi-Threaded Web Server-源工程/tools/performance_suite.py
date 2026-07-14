"""Repeatable worker-pool performance experiment."""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from html import escape
import socket
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Sequence


@dataclass(frozen=True, slots=True)
class RunResult:
    workers: int
    repetition: int
    requests: int
    concurrency: int
    duration_seconds: float
    throughput: float
    mean_ms: float
    median_ms: float
    p95_ms: float
    successes: int
    errors: int


@dataclass(frozen=True, slots=True)
class SummaryResult:
    workers: int
    throughput: float
    mean_ms: float
    median_ms: float
    p95_ms: float
    errors: int


def percentile(values: list[float], percent: float) -> float:
    if not values:
        raise ValueError("percentile requires at least one value")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    ordered = sorted(values)
    position = (len(ordered) - 1) * percent / 100
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def summarize(rows: list[RunResult]) -> list[SummaryResult]:
    grouped: dict[int, list[RunResult]] = {}
    for row in rows:
        grouped.setdefault(row.workers, []).append(row)
    return [
        SummaryResult(
            workers=workers,
            throughput=statistics.median(row.throughput for row in group),
            mean_ms=statistics.median(row.mean_ms for row in group),
            median_ms=statistics.median(row.median_ms for row in group),
            p95_ms=statistics.median(row.p95_ms for row in group),
            errors=sum(row.errors for row in group),
        )
        for workers, group in sorted(grouped.items())
    ]


def fetch_http10(
    address: tuple[str, int],
    target: str,
    expected_body: bytes,
    timeout: float = 10.0,
) -> tuple[float, bool]:
    started = time.perf_counter()
    try:
        with socket.create_connection(address, timeout=timeout) as client:
            client.settimeout(timeout)
            request = (
                f"GET {target} HTTP/1.0\r\n"
                f"Host: {address[0]}:{address[1]}\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii")
            client.sendall(request)
            chunks: list[bytes] = []
            while True:
                chunk = client.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)
        wire = b"".join(chunks)
        raw_headers, body = wire.split(b"\r\n\r\n", 1)
        status = int(raw_headers.split(b"\r\n", 1)[0].split()[1])
        success = status == 200 and body == expected_body
    except (OSError, ValueError, IndexError):
        success = False
    elapsed_ms = (time.perf_counter() - started) * 1000
    return elapsed_ms, success


def benchmark_once(
    address: tuple[str, int],
    expected_body: bytes,
    *,
    workers: int,
    repetition: int,
    request_count: int,
    concurrency: int,
) -> RunResult:
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        outcomes = list(
            pool.map(
                lambda _: fetch_http10(address, "/index.html", expected_body),
                range(request_count),
            )
        )
    duration = time.perf_counter() - started
    latencies = [latency for latency, _ in outcomes]
    successes = sum(1 for _, success in outcomes if success)
    return RunResult(
        workers=workers,
        repetition=repetition,
        requests=request_count,
        concurrency=concurrency,
        duration_seconds=duration,
        throughput=request_count / duration,
        mean_ms=statistics.fmean(latencies),
        median_ms=statistics.median(latencies),
        p95_ms=percentile(latencies, 95),
        successes=successes,
        errors=request_count - successes,
    )


def write_svg(
    path: Path,
    rows: list[SummaryResult],
    *,
    metric: str,
    title: str,
    y_label: str,
) -> None:
    if not rows:
        raise ValueError("cannot chart empty results")
    attribute = {
        "throughput": "throughput",
        "mean_ms": "mean_ms",
        "median_ms": "median_ms",
        "p95_ms": "p95_ms",
    }[metric]
    values = [float(getattr(row, attribute)) for row in rows]
    width, height = 900, 520
    left, right, top, bottom = 90, 35, 65, 75
    plot_width = width - left - right
    plot_height = height - top - bottom
    maximum = max(values) * 1.1 or 1.0
    points: list[tuple[float, float]] = []
    for index, value in enumerate(values):
        x = left + (plot_width * index / max(1, len(rows) - 1))
        y = top + plot_height * (1 - value / maximum)
        points.append((x, y))

    grid = []
    for index in range(6):
        value = maximum * index / 5
        y = top + plot_height * (1 - index / 5)
        grid.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#dbe3ee"/>')
        grid.append(f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end" font-size="12" fill="#526174">{value:.1f}</text>')
    point_string = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    markers = []
    for row, value, (x, y) in zip(rows, values, points):
        markers.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#2563eb"/>')
        markers.append(f'<text x="{x:.1f}" y="{height-bottom+25}" text-anchor="middle" font-size="13">{row.workers}</text>')
        markers.append(f'<text x="{x:.1f}" y="{y-11:.1f}" text-anchor="middle" font-size="12" fill="#1e3a8a">{value:.2f}</text>')
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        '<rect width="100%" height="100%" fill="white"/>'
        f'<text x="{width/2}" y="32" text-anchor="middle" font-family="sans-serif" font-size="22" font-weight="700">{escape(title)}</text>'
        f'<text x="22" y="{height/2}" transform="rotate(-90 22 {height/2})" text-anchor="middle" font-family="sans-serif" font-size="13">{escape(y_label)}</text>'
        + "".join(grid)
        + f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#526174"/>'
        + f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#526174"/>'
        + f'<polyline points="{point_string}" fill="none" stroke="#2563eb" stroke-width="3"/>'
        + "".join(markers)
        + f'<text x="{width/2}" y="{height-18}" text-anchor="middle" font-family="sans-serif" font-size="13">worker threads</text>'
        + "</svg>"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def wait_for_server(process: subprocess.Popen, address: tuple[str, int], timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"server exited with code {process.returncode}")
        try:
            with socket.create_connection(address, timeout=0.1):
                return
        except OSError:
            time.sleep(0.02)
    raise TimeoutError("server did not start before timeout")


def write_results(output_dir: Path, runs: list[RunResult], summary: list[SummaryResult]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_csv = output_dir / "performance.csv"
    with run_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(runs[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in runs)
    markdown = [
        "# Worker Thread Performance Summary",
        "",
        "| Workers | Throughput (req/s) | Mean (ms) | Median (ms) | P95 (ms) | Errors |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    markdown.extend(
        f"| {row.workers} | {row.throughput:.2f} | {row.mean_ms:.2f} | {row.median_ms:.2f} | {row.p95_ms:.2f} | {row.errors} |"
        for row in summary
    )
    (output_dir / "performance.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    write_svg(output_dir / "throughput.svg", summary, metric="throughput", title="Static Page Throughput", y_label="requests / second")
    write_svg(output_dir / "latency.svg", summary, metric="p95_ms", title="Static Page P95 Latency", y_label="milliseconds")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", nargs="+", type=int, default=[1, 2, 4, 8, 12, 16, 20])
    parser.add_argument("--requests", type=int, default=500)
    parser.add_argument("--concurrency", type=int, default=40)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if min(arguments.workers) < 1 or min(arguments.requests, arguments.concurrency, arguments.repetitions) < 1 or arguments.warmup < 0:
        raise SystemExit("worker, request, concurrency and repetition values must be positive")
    project_root = Path(__file__).resolve().parents[1]
    expected_body = (project_root / "webroot" / "index.html").read_bytes()
    runs: list[RunResult] = []
    for worker_count in arguments.workers:
        port = find_free_port()
        address = ("127.0.0.1", port)
        command = [
            sys.executable,
            str(project_root / "web_server.py"),
            "--host", "127.0.0.1",
            "--port", str(port),
            "--workers", str(worker_count),
            "--max-connections", "128",
        ]
        process = subprocess.Popen(command, cwd=project_root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            wait_for_server(process, address)
            for _ in range(arguments.warmup):
                fetch_http10(address, "/index.html", expected_body)
            for repetition in range(1, arguments.repetitions + 1):
                result = benchmark_once(
                    address,
                    expected_body,
                    workers=worker_count,
                    repetition=repetition,
                    request_count=arguments.requests,
                    concurrency=arguments.concurrency,
                )
                runs.append(result)
                print(
                    f"workers={worker_count:2d} repetition={repetition} "
                    f"throughput={result.throughput:.2f} req/s p95={result.p95_ms:.2f} ms errors={result.errors}"
                )
        finally:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
    summary = summarize(runs)
    write_results(arguments.output_dir, runs, summary)
    if any(row.errors for row in runs):
        print("Performance run completed with request errors.")
        return 1
    print(f"Results written to {arguments.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
