#!/usr/bin/env python3
"""Verify unpacked MSD task directories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def verify_task(task_dir: Path) -> list[str]:
    problems: list[str] = []
    dataset_json = task_dir / "dataset.json"
    if not dataset_json.is_file():
        problems.append(f"{task_dir.name}: missing dataset.json")
        return problems
    try:
        metadata = json.loads(dataset_json.read_text())
    except json.JSONDecodeError as exc:
        problems.append(f"{task_dir.name}: invalid dataset.json: {exc}")
        return problems
    if not (task_dir / "imagesTr").is_dir():
        problems.append(f"{task_dir.name}: missing imagesTr")
    if not (task_dir / "labelsTr").is_dir():
        problems.append(f"{task_dir.name}: missing labelsTr")
    for item in metadata.get("training", []):
        image = task_dir / item.get("image", "")
        label = task_dir / item.get("label", "")
        if not image.is_file():
            problems.append(f"{task_dir.name}: missing training image {image}")
        if not label.is_file():
            problems.append(f"{task_dir.name}: missing training label {label}")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    dataset_root = args.dataset_root.resolve()
    extracted_dir = dataset_root / "data" / "raw" / "extracted"
    task_dirs = sorted(path for path in extracted_dir.iterdir() if path.is_dir()) if extracted_dir.exists() else []
    problems: list[str] = []
    for task_dir in task_dirs:
        problems.extend(verify_task(task_dir))

    print(f"tasks={len(task_dirs)}")
    if problems:
        print("status=failed")
        for problem in problems[:200]:
            print(problem)
        if len(problems) > 200:
            print(f"... {len(problems) - 200} more problems")
        raise SystemExit(1)
    print("status=ok")


if __name__ == "__main__":
    main()
