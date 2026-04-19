#!/usr/bin/env python3
"""Create deterministic train/val/test splits from the manifest."""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


def parse_ratios(value: str) -> tuple[float, float, float]:
    parts = [float(part) for part in value.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("ratios must have three comma-separated values")
    total = sum(parts)
    if total <= 0:
        raise argparse.ArgumentTypeError("ratios must sum to a positive value")
    return tuple(part / total for part in parts)  # type: ignore[return-value]


def read_complete_cases(manifest_path: Path) -> list[str]:
    with manifest_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return [row["case_id"] for row in reader if row.get("complete") == "1"]


def split_cases(
    case_ids: list[str],
    ratios: tuple[float, float, float],
    seed: int,
) -> dict[str, list[str]]:
    shuffled = list(case_ids)
    random.Random(seed).shuffle(shuffled)

    total = len(shuffled)
    train_count = int(total * ratios[0])
    val_count = int(total * ratios[1])

    train = sorted(shuffled[:train_count])
    val = sorted(shuffled[train_count : train_count + val_count])
    test = sorted(shuffled[train_count + val_count :])
    return {"train": train, "val": val, "test": test}


def write_splits(splits: dict[str, list[str]], output_dir: Path, seed: int, ratios: tuple[float, float, float]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for split_name, case_ids in splits.items():
        path = output_dir / f"{split_name}.txt"
        path.write_text("".join(f"{case_id}\n" for case_id in case_ids))

    with (output_dir / "split.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["case_id", "split"])
        for split_name in ["train", "val", "test"]:
            for case_id in splits[split_name]:
                writer.writerow([case_id, split_name])

    metadata = [
        f"seed: {seed}",
        f"ratios: {ratios[0]:.6f},{ratios[1]:.6f},{ratios[2]:.6f}",
        f"train: {len(splits['train'])}",
        f"val: {len(splits['val'])}",
        f"test: {len(splits['test'])}",
    ]
    (output_dir / "split.yaml").write_text("\n".join(metadata) + "\n")


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
        "--output-dir",
        type=Path,
        default=None,
        help="Split output directory. Defaults to data/splits/default.",
    )
    parser.add_argument("--ratios", type=parse_ratios, default=parse_ratios("0.8,0.1,0.1"))
    parser.add_argument("--seed", type=int, default=20260419)
    args = parser.parse_args()

    dataset_root = args.dataset_root.resolve()
    manifest = args.manifest or dataset_root / "data" / "manifests" / "manifest.csv"
    output_dir = args.output_dir or dataset_root / "data" / "splits" / "default"

    case_ids = read_complete_cases(manifest.resolve())
    splits = split_cases(case_ids, args.ratios, args.seed)
    write_splits(splits, output_dir.resolve(), args.seed, args.ratios)

    print(f"wrote {output_dir.resolve()}")
    print(
        " ".join(
            [
                f"total={len(case_ids)}",
                f"train={len(splits['train'])}",
                f"val={len(splits['val'])}",
                f"test={len(splits['test'])}",
                f"seed={args.seed}",
            ]
        )
    )


if __name__ == "__main__":
    main()
