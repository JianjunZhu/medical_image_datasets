#!/usr/bin/env python3
"""Verify TotalSegmentator downloaded archives and extracted directories."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


EXPECTED = {
    "ct": {
        "file": "Totalsegmentator_dataset_v201.zip",
        "size": 23581218285,
        "md5": "fe250e5718e0a3b5df4c4ea9d58a62fe",
    },
    "mri": {
        "file": "TotalsegmentatorMRI_dataset_v200.zip",
        "size": 5100514630,
        "md5": "54638f4cb883ce3b34225195358c398f",
    },
    "ct_small": {
        "file": "Totalsegmentator_dataset_small_v201.zip",
        "size": None,
        "md5": "6b5524af4b15e6ba06ef2d700c0c73e0",
    },
}


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(archives_dir: Path, subset: str, check_md5: bool) -> list[str]:
    expected = EXPECTED[subset]
    path = archives_dir / expected["file"]
    problems: list[str] = []
    if not path.is_file():
        return [f"{subset}: missing archive {path}"]
    if expected["size"] is not None and path.stat().st_size != expected["size"]:
        problems.append(
            f"{subset}: size mismatch expected={expected['size']} actual={path.stat().st_size}"
        )
    if not zipfile.is_zipfile(path):
        problems.append(f"{subset}: not a valid zip file")
    if check_md5 and md5(path) != expected["md5"]:
        problems.append(f"{subset}: md5 mismatch")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--subsets", default="ct,mri")
    parser.add_argument("--check-md5", action="store_true")
    args = parser.parse_args()

    dataset_root = args.dataset_root.resolve()
    archives_dir = dataset_root / "data" / "raw" / "archives"
    extracted_dir = dataset_root / "data" / "raw" / "extracted"
    subsets = [item.strip() for item in args.subsets.split(",") if item.strip()]
    problems: list[str] = []
    for subset in subsets:
        if subset not in EXPECTED:
            problems.append(f"unsupported subset={subset}")
            continue
        problems.extend(verify_archive(archives_dir, subset, args.check_md5))

    extracted = sorted(path.name for path in extracted_dir.iterdir() if path.is_dir()) if extracted_dir.exists() else []
    print(json.dumps({"subsets": subsets, "extracted_dirs": extracted}, indent=2))
    if problems:
        print("status=failed")
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print("status=ok")


if __name__ == "__main__":
    main()
