from __future__ import annotations

import argparse
from pathlib import Path
import random


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic binary test data.")
    parser.add_argument("path")
    parser.add_argument("--size", type=int, default=3 * 1024 * 1024 + 123)
    parser.add_argument("--seed", type=int, default=1120231863)
    args = parser.parse_args()
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


if __name__ == "__main__":
    main()

