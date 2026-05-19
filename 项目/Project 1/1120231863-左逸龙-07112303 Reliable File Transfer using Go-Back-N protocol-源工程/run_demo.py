from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import threading
import time

from gbn.host import Host, sha256_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local two-host full-duplex demo.")
    parser.add_argument("--host1", default="configs/host1.json")
    parser.add_argument("--host2", default="configs/host2.json")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
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
    time.sleep(2.0)
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
            print(f"{src} -> {dst}: {'OK' if sha256_file(src) == sha256_file(dst) else 'MISMATCH'}")


if __name__ == "__main__":
    main()
