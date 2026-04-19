#!/usr/bin/env python3
"""Verify the local AbdomenAtlas1.0Mini file layout."""

from __future__ import annotations

import argparse
import csv
import gzip
from collections import Counter
from pathlib import Path


ORGANS = [
    "aorta",
    "gall_bladder",
    "kidney_left",
    "kidney_right",
    "liver",
    "pancreas",
    "postcava",
    "spleen",
    "stomach",
]

EXPECTED_COLUMNS = [
    "case_id",
    "case_dir",
    "ct",
    "combined_labels",
    *[f"seg_{organ}" for organ in ORGANS],
    "complete",
]


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        missing_columns = [name for name in EXPECTED_COLUMNS if name not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"manifest is missing columns: {', '.join(missing_columns)}")
        return list(reader)


def looks_like_gzip(path: Path) -> bool:
    with path.open("rb") as handle:
        return handle.read(2) == b"\x1f\x8b"


def can_open_gzip(path: Path) -> bool:
    with gzip.open(path, "rb") as handle:
        handle.read(1)
    return True


def default_raw_dir(dataset_root: Path) -> Path:
    raw_dir = dataset_root / "data" / "raw"
    if any(raw_dir.glob("BDMAP_*")):
        return raw_dir
    return dataset_root


def verify_manifest(
    dataset_root: Path,
    manifest_path: Path,
    raw_dir: Path,
    deep_gzip: bool,
) -> tuple[int, Counter[str]]:
    rows = read_manifest(manifest_path)
    problems: Counter[str] = Counter()
    seen_case_ids: set[str] = set()

    for row in rows:
        case_id = row["case_id"]
        if case_id in seen_case_ids:
            problems["duplicate_case_id"] += 1
        seen_case_ids.add(case_id)

        case_dir = dataset_root / row["case_dir"]
        if not case_dir.is_dir():
            problems["missing_case_dir"] += 1

        file_columns = ["ct", "combined_labels", *[f"seg_{organ}" for organ in ORGANS]]
        complete = True
        for column in file_columns:
            path = dataset_root / row[column]
            if not path.is_file():
                problems[f"missing_{column}"] += 1
                complete = False
                continue
            if path.stat().st_size <= 0:
                problems[f"empty_{column}"] += 1
                complete = False
            if not looks_like_gzip(path):
                problems[f"bad_gzip_magic_{column}"] += 1
                complete = False
            if deep_gzip:
                try:
                    can_open_gzip(path)
                except OSError:
                    problems[f"bad_gzip_stream_{column}"] += 1
                    complete = False

        if row["complete"] not in {"0", "1"}:
            problems["invalid_complete_value"] += 1
        elif int(row["complete"]) != int(complete):
            problems["complete_mismatch"] += 1

    case_dirs = sorted(path.name for path in raw_dir.glob("BDMAP_*") if path.is_dir())
    if len(case_dirs) != len(rows):
        problems["case_count_mismatch"] += abs(len(case_dirs) - len(rows))

    manifest_ids = {row["case_id"] for row in rows}
    dir_ids = set(case_dirs)
    problems["case_dir_not_in_manifest"] += len(dir_ids - manifest_ids)
    problems["manifest_case_not_on_disk"] += len(manifest_ids - dir_ids)
    return len(rows), problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the AbdomenAtlas1.0Mini dataset root.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Manifest path. Defaults to data/manifests/manifest.csv.",
    )
    parser.add_argument(
        "--deep-gzip",
        action="store_true",
        help="Open every gzip stream. Slower, but catches truncated files.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Directory containing BDMAP_* cases. Defaults to data/raw when populated.",
    )
    args = parser.parse_args()

    dataset_root = args.dataset_root.resolve()
    raw_dir = args.raw_dir.resolve() if args.raw_dir else default_raw_dir(dataset_root)
    manifest = args.manifest or dataset_root / "data" / "manifests" / "manifest.csv"
    total, problems = verify_manifest(dataset_root, manifest.resolve(), raw_dir, args.deep_gzip)
    problem_total = sum(problems.values())

    print(f"dataset_root={dataset_root}")
    print(f"raw_dir={raw_dir}")
    print(f"manifest={manifest}")
    print(f"cases={total}")
    if problem_total == 0:
        print("status=ok")
        return

    print("status=failed")
    for key, count in sorted(problems.items()):
        if count:
            print(f"{key}={count}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
