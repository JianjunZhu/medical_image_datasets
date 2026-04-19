#!/usr/bin/env python3
"""Build a coarse file manifest for extracted TotalSegmentator data."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    dataset_root = args.dataset_root.resolve()
    extracted_dir = dataset_root / "data" / "raw" / "extracted"
    output = args.output or dataset_root / "data" / "manifests" / "manifest.csv"
    output.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str | int]] = []
    if extracted_dir.exists():
        for path in sorted(extracted_dir.rglob("*")):
            if path.is_file() and not path.name.startswith("._"):
                rows.append(
                    {
                        "path": str(path.relative_to(dataset_root)),
                        "file_name": path.name,
                        "suffix": "".join(path.suffixes),
                        "bytes": path.stat().st_size,
                    }
                )

    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "file_name", "suffix", "bytes"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {output}")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
