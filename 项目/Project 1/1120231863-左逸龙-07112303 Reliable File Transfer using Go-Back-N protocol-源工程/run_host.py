from __future__ import annotations

import argparse

from gbn.host import Host


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one UDP Go-Back-N host.")
    parser.add_argument("config", help="Path to host JSON config")
    parser.add_argument("--linger", type=float, default=2.0, help="Seconds to keep receiving after senders finish")
    args = parser.parse_args()
    Host(args.config).start(wait=True, linger=args.linger)


if __name__ == "__main__":
    main()

