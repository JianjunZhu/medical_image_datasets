"""Path-level dataset interface for unpacked MSD tasks."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class MSDCase:
    task_name: str
    case_id: str
    split: str
    image: Path
    label: Path | None = None
    task_dir: Path | None = None
    dataset_json: Path | None = None

    @property
    def complete(self) -> bool:
        return self.image.is_file() and (self.label is None or self.label.is_file())

    @property
    def has_label(self) -> bool:
        return self.label is not None

    def to_dict(self, relative_to: Path | None = None) -> dict[str, str | int]:
        def format_path(path: Path | None) -> str:
            if path is None:
                return ""
            if relative_to is not None:
                return str(path.relative_to(relative_to))
            return str(path)

        return {
            "task_name": self.task_name,
            "case_id": self.case_id,
            "split": self.split,
            "task_dir": format_path(self.task_dir),
            "dataset_json": format_path(self.dataset_json),
            "image": format_path(self.image),
            "label": format_path(self.label),
            "image_exists": int(self.image.is_file()),
            "label_exists": int(self.label.is_file()) if self.label is not None else 0,
            "complete": int(self.complete),
        }

    def require_complete(self) -> "MSDCase":
        missing = [str(self.image)] if not self.image.is_file() else []
        if self.label is not None and not self.label.is_file():
            missing.append(str(self.label))
        if missing:
            key = f"{self.task_name}/{self.case_id}/{self.split}"
            raise FileNotFoundError(
                f"{key} is incomplete; missing {len(missing)} files: {missing[:3]}"
            )
        return self


class MSDIndex:
    def __init__(
        self,
        dataset_root: str | Path,
        *,
        manifest_path: str | Path | None = None,
        task: str | None = None,
        split: str | None = None,
        case_ids: Iterable[str] | None = None,
        complete_only: bool = False,
    ):
        self.dataset_root = Path(dataset_root).expanduser().resolve()
        self.extracted_dir = self.dataset_root / "data" / "raw" / "extracted"
        self.manifest_path = (
            Path(manifest_path).expanduser().resolve()
            if manifest_path is not None
            else self.dataset_root / "data" / "manifests" / "manifest.csv"
        )
        allowed = set(case_ids) if case_ids is not None else None
        self.records = (
            self._load_manifest(self.manifest_path)
            if self.manifest_path.is_file()
            else self._load_from_dirs()
        )
        if task is not None:
            self.records = [record for record in self.records if record.task_name == task]
        if split is not None:
            self.records = [record for record in self.records if record.split == split]
        if allowed is not None:
            self.records = [record for record in self.records if record.case_id in allowed]
        if complete_only:
            self.records = [record for record in self.records if record.complete]
        self.records = sorted(
            self.records,
            key=lambda record: (record.task_name, record.split, record.case_id),
        )
        self._by_key = {(record.task_name, record.case_id, record.split): record for record in self.records}

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self):
        for index in range(len(self)):
            yield self[index]

    def __getitem__(self, index: int) -> MSDCase:
        return self.records[index]

    def get(self, task_name: str, case_id: str, split: str = "train") -> MSDCase:
        return self._by_key[(task_name, case_id, split)]

    def case_ids(self) -> list[str]:
        return [record.case_id for record in self.records]

    def tasks(self) -> list[str]:
        return sorted({record.task_name for record in self.records})

    def splits(self) -> list[str]:
        return sorted({record.split for record in self.records})

    def by_task(self, task_name: str) -> list[MSDCase]:
        return [record for record in self.records if record.task_name == task_name]

    def by_split(self, split: str) -> list[MSDCase]:
        return [record for record in self.records if record.split == split]

    def task_dir(self, task_name: str) -> Path:
        return self.extracted_dir / task_name

    def task_metadata(self, task_name: str) -> dict:
        dataset_json = self.task_dir(task_name) / "dataset.json"
        if not dataset_json.is_file():
            raise FileNotFoundError(f"missing dataset.json for {task_name}: {dataset_json}")
        return json.loads(dataset_json.read_text())

    @classmethod
    def from_split(
        cls,
        dataset_root: str | Path,
        split_file: str | Path,
        *,
        manifest_path: str | Path | None = None,
        task: str | None = None,
        complete_only: bool = False,
    ) -> "MSDIndex":
        case_ids = [
            line.strip().split(",")[0]
            for line in Path(split_file).expanduser().read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        return cls(
            dataset_root,
            manifest_path=manifest_path,
            task=task,
            case_ids=case_ids,
            complete_only=complete_only,
        )

    def _load_manifest(self, manifest_path: Path) -> list[MSDCase]:
        records: list[MSDCase] = []
        with manifest_path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                task_dir = self.extracted_dir / row["task_name"]
                label = self.dataset_root / row["label"] if row.get("label") else None
                records.append(
                    MSDCase(
                        task_name=row["task_name"],
                        case_id=row["case_id"],
                        split=row["split"],
                        image=self.dataset_root / row["image"],
                        label=label,
                        task_dir=task_dir,
                        dataset_json=task_dir / "dataset.json",
                    )
                )
        return records

    def _load_from_dirs(self) -> list[MSDCase]:
        records: list[MSDCase] = []
        if not self.extracted_dir.exists():
            return records
        for task_dir in sorted(path for path in self.extracted_dir.iterdir() if path.is_dir()):
            dataset_json = task_dir / "dataset.json"
            if not dataset_json.is_file():
                continue
            metadata = json.loads(dataset_json.read_text())
            for item in metadata.get("training", []):
                image = task_dir / item["image"]
                label = task_dir / item["label"]
                records.append(
                    MSDCase(
                        task_name=task_dir.name,
                        case_id=Path(item["image"]).name.replace(".nii.gz", ""),
                        split="train",
                        image=image,
                        label=label,
                        task_dir=task_dir,
                        dataset_json=dataset_json,
                    )
                )
            images_ts = task_dir / "imagesTs"
            if images_ts.is_dir():
                for image in sorted(images_ts.glob("*.nii.gz")):
                    if image.name.startswith("._"):
                        continue
                    records.append(
                        MSDCase(
                            task_name=task_dir.name,
                            case_id=image.name.replace(".nii.gz", ""),
                            split="test",
                            image=image,
                            label=None,
                            task_dir=task_dir,
                            dataset_json=dataset_json,
                        )
                    )
        return records
