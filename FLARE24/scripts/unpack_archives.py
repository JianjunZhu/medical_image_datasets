#!/usr/bin/env python
"""Unpack nested FLARE24 archives from raw Hugging Face snapshots."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import zipfile
from pathlib import Path


def unpack_zip(path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as archive:
        archive.extractall(output_dir)


def unpack_7z(path: Path, output_dir: Path) -> None:
    if shutil.which("7z") is None:
        raise RuntimeError(f"7z is required to unpack {path}")
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["7z", "x", f"-o{output_dir}", str(path), "-y"], check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    raw_dir = args.root / "data" / "raw" / "huggingface"
    extracted_dir = args.root / "data" / "raw" / "extracted"
    archives = sorted([*raw_dir.rglob("*.zip"), *raw_dir.rglob("*.7z")])
    unpacked = 0
    skipped = 0
    for archive in archives:
        rel = archive.relative_to(raw_dir)
        output_dir = extracted_dir / rel.parent / archive.stem
        if output_dir.exists() and any(output_dir.iterdir()) and not args.overwrite:
            skipped += 1
            continue
        if archive.suffix.lower() == ".zip":
            unpack_zip(archive, output_dir)
        elif archive.suffix.lower() == ".7z":
            unpack_7z(archive, output_dir)
        unpacked += 1
    print(f"archives={len(archives)} unpacked={unpacked} skipped={skipped} output={extracted_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
