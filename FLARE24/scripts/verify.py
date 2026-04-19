#!/usr/bin/env python
"""Verify FLARE24 raw snapshots and extracted layout."""

from __future__ import annotations

import argparse
from pathlib import Path


TASK_DIRS = {
    "task1": "FLARE-Task1-Pancancer",
    "task2": "FLARE-Task2-LaptopSeg",
    "task3": "FLARE-Task3-DomainAdaption",
}


def count_files(root: Path, pattern: str) -> int:
    return sum(1 for _ in root.rglob(pattern)) if root.exists() else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--tasks", default="task1,task2,task3")
    args = parser.parse_args()

    raw_dir = args.root / "data" / "raw" / "huggingface"
    extracted_dir = args.root / "data" / "raw" / "extracted"
    requested = [item.strip() for item in args.tasks.split(",") if item.strip()]
    missing: list[str] = []
    total_images = 0
    total_archives = 0

    for task in requested:
        dirname = TASK_DIRS.get(task)
        if dirname is None:
            missing.append(f"unsupported task {task}")
            continue
        task_dir = raw_dir / dirname
        if not task_dir.is_dir():
            missing.append(f"missing raw snapshot {task}: {task_dir}")
            continue
        images = count_files(task_dir, "*.nii.gz")
        archives = count_files(task_dir, "*.zip") + count_files(task_dir, "*.7z")
        total_images += images
        total_archives += archives
        print(f"{task}: raw_dir={task_dir} nifti={images} nested_archives={archives}")

    extracted_archives = count_files(extracted_dir, "*.nii.gz")
    print(f"summary: tasks={len(requested)} nifti={total_images} nested_archives={total_archives} extracted_nifti={extracted_archives}")
    if missing:
        print("status=missing")
        for item in missing:
            print(f"missing: {item}")
        return 1
    print("status=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
