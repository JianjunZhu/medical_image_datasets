#!/usr/bin/env python3
"""Unpack downloaded MSD archives into data/raw/extracted."""

from __future__ import annotations

import argparse
import shutil
import tarfile
import zipfile
from pathlib import Path


def unpack_archive(path: Path, output_dir: Path, force: bool) -> str:
    target = output_dir / path.name
    for suffix in [".tar.gz", ".tgz", ".tar", ".zip"]:
        if target.name.endswith(suffix):
            target = output_dir / target.name[: -len(suffix)]
            break
    if target.exists() and not force:
        return f"skip existing {target}"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    if tarfile.is_tarfile(path):
        with tarfile.open(path) as archive:
            archive.extractall(target)
    elif zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            archive.extractall(target)
    else:
        return f"skip unsupported {path}"
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

    for path in sorted(item for item in archives_dir.rglob("*") if item.is_file()):
        print(unpack_archive(path, extracted_dir, args.force))


if __name__ == "__main__":
    main()
