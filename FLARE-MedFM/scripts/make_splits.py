#!/usr/bin/env python
"""Create optional deterministic downstream splits from the FLARE-MedFM manifest."""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--dataset", default="")
    parser.add_argument("--ratios", default="0.8,0.1,0.1")
    parser.add_argument("--seed", type=int, default=20260419)
    parser.add_argument("--name", default="default")
    args = parser.parse_args()

    manifest = args.manifest or args.root / "data" / "manifests" / "manifest.csv"
    ratios = [float(item) for item in args.ratios.split(",")]
    if len(ratios) != 3:
        raise ValueError("--ratios must contain train,val,test")
    rows = list(csv.DictReader(manifest.open()))
    rows = [row for row in rows if row["split"] == "train" and row["has_label"] == "1"]
    if args.dataset:
        rows = [row for row in rows if row["dataset"] == args.dataset]
    case_ids = sorted({row["case_id"] for row in rows})
    random.Random(args.seed).shuffle(case_ids)
    n = len(case_ids)
    n_train = int(n * ratios[0])
    n_val = int(n * ratios[1])
    splits = {
        "train": sorted(case_ids[:n_train]),
        "val": sorted(case_ids[n_train : n_train + n_val]),
        "test": sorted(case_ids[n_train + n_val :]),
    }
    out_dir = args.root / "data" / "splits" / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    for split, ids in splits.items():
        (out_dir / f"{split}.txt").write_text("\n".join(ids) + ("\n" if ids else ""))
    with (out_dir / "split.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["case_id", "split"])
        for split, ids in splits.items():
            for case_id in ids:
                writer.writerow([case_id, split])
    (out_dir / "split.yaml").write_text(
        f"name: {args.name}\nseed: {args.seed}\nratios: {args.ratios}\ndataset: {args.dataset or 'all'}\n"
    )
    print(f"cases={n} output={out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
