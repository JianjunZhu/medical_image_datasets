#!/usr/bin/env python3
"""Build a manifest from unpacked MSD task directories."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def task_rows(dataset_root: Path, task_dir: Path) -> list[dict[str, str | int]]:
    dataset_json = task_dir / "dataset.json"
    if not dataset_json.is_file():
        return []
    metadata = json.loads(dataset_json.read_text())
    rows: list[dict[str, str | int]] = []
    for item in metadata.get("training", []):
        image = task_dir / item["image"]
        label = task_dir / item["label"]
        rows.append(
            {
                "task_name": task_dir.name,
                "case_id": Path(item["image"]).name.replace(".nii.gz", ""),
                "split": "train",
                "image": str(image.relative_to(dataset_root)),
                "label": str(label.relative_to(dataset_root)),
                "image_exists": int(image.is_file()),
                "label_exists": int(label.is_file()),
            }
        )
    images_ts = task_dir / "imagesTs"
    if images_ts.is_dir():
        for image in sorted(images_ts.glob("*.nii.gz")):
            if image.name.startswith("._"):
                continue
            rows.append(
                {
                    "task_name": task_dir.name,
                    "case_id": image.name.replace(".nii.gz", ""),
                    "split": "test",
                    "image": str(image.relative_to(dataset_root)),
                    "label": "",
                    "image_exists": int(image.is_file()),
                    "label_exists": 0,
                }
            )
    return rows


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
        for task_dir in sorted(path for path in extracted_dir.iterdir() if path.is_dir()):
            rows.extend(task_rows(dataset_root, task_dir))

    fieldnames = ["task_name", "case_id", "split", "image", "label", "image_exists", "label_exists"]
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {output}")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
