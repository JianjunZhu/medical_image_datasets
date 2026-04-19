#!/usr/bin/env python
"""Build a lightweight FLARE24 NIfTI manifest."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


TASK_DIRS = {
    "FLARE-Task1-Pancancer": "task1",
    "FLARE-Task2-LaptopSeg": "task2",
    "FLARE-Task3-DomainAdaption": "task3",
}


def strip_nii_gz(path: Path) -> str:
    name = path.name
    return name[:-7] if name.endswith(".nii.gz") else path.stem


def case_id_from_image(path: Path) -> str:
    case_id = strip_nii_gz(path)
    return case_id[:-5] if case_id.endswith("_0000") else case_id


def infer_split(parts: tuple[str, ...]) -> str:
    joined = "/".join(parts).lower()
    if "validation" in joined or "imagesval" in joined or "labelsval" in joined:
        return "validation"
    if "coreset" in joined:
        return "coreset"
    if "train" in joined:
        return "train"
    return "unknown"


def infer_label_type(parts: tuple[str, ...], has_label: bool) -> str:
    joined = "/".join(parts).lower()
    if not has_label:
        return "unlabeled"
    if "pseudo" in joined:
        return "pseudo"
    if "public" in joined:
        return "public"
    if "hidden" in joined:
        return "hidden"
    return "ground_truth"


def infer_modality(parts: tuple[str, ...]) -> str:
    joined = "/".join(parts).lower()
    if "mri" in joined:
        return "MRI"
    if "pet" in joined:
        return "PET"
    return "CT"


def build_label_index(search_roots: list[Path], dataset_root: Path) -> dict[tuple[str, str], Path]:
    labels: dict[tuple[str, str], Path] = {}
    for root in search_roots:
        if not root.exists():
            continue
        for path in root.rglob("*.nii.gz"):
            if path.name.startswith("._"):
                continue
            rel = path.relative_to(dataset_root)
            lower = "/".join(rel.parts).lower()
            if "label" not in lower and "mask" not in lower and "seg" not in lower:
                continue
            task = next((value for key, value in TASK_DIRS.items() if key in rel.parts), "")
            if not task:
                continue
            labels[(task, strip_nii_gz(path))] = path
    return labels


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    root = args.root.resolve()
    raw_dir = root / "data" / "raw" / "huggingface"
    extracted_dir = root / "data" / "raw" / "extracted"
    output = args.output or root / "data" / "manifests" / "manifest.csv"
    output.parent.mkdir(parents=True, exist_ok=True)

    search_roots = [raw_dir, extracted_dir]
    label_index = build_label_index(search_roots, root)
    rows: list[dict[str, str | int]] = []

    for search_root in search_roots:
        if not search_root.exists():
            continue
        for image in sorted(search_root.rglob("*.nii.gz")):
            if image.name.startswith("._"):
                continue
            rel = image.relative_to(root)
            lower = "/".join(rel.parts).lower()
            if "label" in lower or "mask" in lower or "seg" in lower:
                continue
            task = next((value for key, value in TASK_DIRS.items() if key in rel.parts), "")
            task_dir = next((key for key in TASK_DIRS if key in rel.parts), "")
            if not task:
                continue
            case_id = case_id_from_image(image)
            label = label_index.get((task, case_id))
            rows.append(
                {
                    "task": task,
                    "task_dir": task_dir,
                    "case_id": case_id,
                    "split": infer_split(rel.parts),
                    "modality": infer_modality(rel.parts),
                    "image": str(image.relative_to(root)),
                    "label": str(label.relative_to(root)) if label else "",
                    "has_label": int(label is not None),
                    "label_type": infer_label_type(rel.parts, label is not None),
                    "source_root": str(search_root.relative_to(root)),
                }
            )

    fieldnames = [
        "task",
        "task_dir",
        "case_id",
        "split",
        "modality",
        "image",
        "label",
        "has_label",
        "label_type",
        "source_root",
    ]
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"records={len(rows)} output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
