#!/usr/bin/env python3
"""Unpack downloaded TotalSegmentator archives."""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path


def unpack_zip(path: Path, output_dir: Path, force: bool) -> str:
    target = output_dir / path.name.removesuffix(".zip")
    if target.exists() and not force:
        return f"skip existing {target}"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as archive:
        archive.extractall(target)
    return f"unpacked {path} -> {target}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    dataset_root = args.dataset_root.resolve()
    archives_dir = dataset_root / "data" / "raw" / "archives"
    extracted_dir = dataset_root / "data" / "raw" / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(archives_dir.glob("*.zip")):
        print(unpack_zip(path, extracted_dir, args.force))


if __name__ == "__main__":
    main()
