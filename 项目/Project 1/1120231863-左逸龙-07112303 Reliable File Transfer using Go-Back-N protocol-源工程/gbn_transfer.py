from __future__ import annotations

import argparse
from pathlib import Path
import random
import shutil
import threading
import time

from gbn.analyzer import analyze_dir
from gbn.host import Host, sha256_file


def run_demo(args: argparse.Namespace) -> None:
    if args.clean:
        for name in ("logs", "received", "results"):
            shutil.rmtree(name, ignore_errors=True)

    h1 = Host(args.host1)
    h2 = Host(args.host2)
    t1 = threading.Thread(target=h1.start, kwargs={"wait": False})
    t2 = threading.Thread(target=h2.start, kwargs={"wait": False})

    t1.start()
    time.sleep(0.2)
    t2.start()
    t1.join()
    t2.join()

    while not (h1.senders_done() and h2.senders_done()):
        time.sleep(0.1)

    time.sleep(args.linger)
    h1.stop()
    h2.stop()
    if h1.receiver_thread:
        h1.receiver_thread.join(timeout=1.0)
    if h2.receiver_thread:
        h2.receiver_thread.join(timeout=1.0)

    pairs = [
        ("data/host1.bin", "received/from_host1.bin"),
        ("data/host2.bin", "received/from_host2.bin"),
    ]
    for src, dst in pairs:
        if Path(src).exists() and Path(dst).exists():
            status = "OK" if sha256_file(src) == sha256_file(dst) else "MISMATCH"
            print(f"{src} -> {dst}: {status}")


def run_host(args: argparse.Namespace) -> None:
    Host(args.config).start(wait=True, linger=args.linger)


def run_analyze(args: argparse.Namespace) -> None:
    summaries = analyze_dir(Path(args.log_dir), Path(args.output_dir))
    print(f"analyzed {len(summaries)} log files")


def run_gen(args: argparse.Namespace) -> None:
    path = Path(args.path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    remaining = args.size
    with path.open("wb") as f:
        while remaining > 0:
            n = min(65536, remaining)
            f.write(bytes(rng.randrange(256) for _ in range(n)))
            remaining -= n
    print(f"generated {path} ({args.size} bytes)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reliable file transfer using Go-Back-N over UDP.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("demo", help="run the local two-host full-duplex demo")
    demo.add_argument("--host1", default="configs/host1.json")
    demo.add_argument("--host2", default="configs/host2.json")
    demo.add_argument("--clean", action="store_true")
    demo.add_argument("--linger", type=float, default=2.0, help="seconds to keep receiving after senders finish")
    demo.set_defaults(func=run_demo)

    host = subparsers.add_parser("host", help="run one UDP Go-Back-N host")
    host.add_argument("config", help="path to host JSON config")
    host.add_argument("--linger", type=float, default=2.0, help="seconds to keep receiving after senders finish")
    host.set_defaults(func=run_host)

    analyze = subparsers.add_parser("analyze", help="analyze Go-Back-N CSV logs")
    analyze.add_argument("--log-dir", default="logs")
    analyze.add_argument("--output-dir", default="results")
    analyze.set_defaults(func=run_analyze)

    gen = subparsers.add_parser("gen", help="generate deterministic binary test data")
    gen.add_argument("path")
    gen.add_argument("--size", type=int, default=3 * 1024 * 1024 + 123)
    gen.add_argument("--seed", type=int, default=1120231863)
    gen.set_defaults(func=run_gen)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
