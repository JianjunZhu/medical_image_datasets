#!/usr/bin/env python3
"""Monitor files appearing in data/raw/archives."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path


def snapshot(path: Path) -> tuple[int, int]:
    files = [item for item in path.rglob("*") if item.is_file()]
    return len(files), sum(item.stat().st_size for item in files)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    dataset_root = args.dataset_root.resolve()
    archives_dir = dataset_root / "data" / "raw" / "archives"
    status_file = dataset_root / "data" / "manifests" / "download_status.json"
    previous_bytes: int | None = None
    previous_time: float | None = None

    while True:
        now = time.time()
        file_count, byte_count = snapshot(archives_dir)
        if previous_bytes is None or previous_time is None:
            speed = 0.0
        else:
            elapsed = max(now - previous_time, 1.0)
            speed = max(byte_count - previous_bytes, 0) / elapsed

        timestamp = datetime.now(timezone.utc).astimezone().isoformat()
        print(
            f"[{timestamp}] files={file_count} "
            f"size_gb={byte_count / 1_000_000_000:.2f} "
            f"speed_mb_s={speed / 1_000_000:.2f}",
            flush=True,
        )
        status_file.parent.mkdir(parents=True, exist_ok=True)
        status_file.write_text(
            json.dumps(
                {
                    "dataset": "MSD",
                    "status": "monitoring",
                    "last_checked_at": timestamp,
                    "download_dir": "data/raw/archives",
                    "downloaded_files": file_count,
                    "downloaded_bytes": byte_count,
                    "speed_bytes_per_second": speed,
                },
                indent=2,
            )
            + "\n"
        )

        if args.once:
            return
        previous_bytes = byte_count
        previous_time = now
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
