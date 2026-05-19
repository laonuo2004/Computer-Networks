from __future__ import annotations

import argparse
from pathlib import Path

from gbn.analyzer import analyze_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Go-Back-N CSV logs.")
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument("--output-dir", default="results")
    args = parser.parse_args()
    summaries = analyze_dir(Path(args.log_dir), Path(args.output_dir))
    print(f"analyzed {len(summaries)} log files")


if __name__ == "__main__":
    main()

