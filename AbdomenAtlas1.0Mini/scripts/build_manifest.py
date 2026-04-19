#!/usr/bin/env python3
"""Build a CSV manifest for the current AbdomenAtlas1.0Mini layout."""

from __future__ import annotations

import argparse
import csv
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


def default_raw_dir(dataset_root: Path) -> Path:
    raw_dir = dataset_root / "data" / "raw"
    if any(raw_dir.glob("BDMAP_*")):
        return raw_dir
    return dataset_root


def build_manifest(dataset_root: Path, raw_dir: Path, output_path: Path) -> tuple[int, int]:
    case_dirs = sorted(path for path in raw_dir.glob("BDMAP_*") if path.is_dir())
    output_path.parent.mkdir(parents=True, exist_ok=True)

    missing = 0
    with output_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "case_id",
                "case_dir",
                "ct",
                "combined_labels",
                *[f"seg_{organ}" for organ in ORGANS],
                "complete",
            ]
        )
        for case_dir in case_dirs:
            paths = {
                "ct": case_dir / "ct.nii.gz",
                "combined_labels": case_dir / "combined_labels.nii.gz",
                **{
                    f"seg_{organ}": case_dir / "segmentations" / f"{organ}.nii.gz"
                    for organ in ORGANS
                },
            }
            complete = all(path.is_file() for path in paths.values())
            if not complete:
                missing += 1
            writer.writerow(
                [
                    case_dir.name,
                    case_dir.relative_to(dataset_root),
                    paths["ct"].relative_to(dataset_root),
                    paths["combined_labels"].relative_to(dataset_root),
                    *[
                        paths[f"seg_{organ}"].relative_to(dataset_root)
                        for organ in ORGANS
                    ],
                    int(complete),
                ]
            )

    return len(case_dirs), missing


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the AbdomenAtlas1.0Mini dataset root.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Manifest CSV path. Defaults to data/manifests/manifest.csv.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Directory containing BDMAP_* cases. Defaults to data/raw when populated.",
    )
    args = parser.parse_args()

    dataset_root = args.dataset_root.resolve()
    raw_dir = (args.raw_dir.resolve() if args.raw_dir else default_raw_dir(dataset_root))
    output = args.output or dataset_root / "data" / "manifests" / "manifest.csv"
    total, missing = build_manifest(dataset_root, raw_dir, output)
    print(f"wrote {output}")
    print(f"raw_dir={raw_dir}")
    print(f"cases={total} incomplete={missing}")


if __name__ == "__main__":
    main()
