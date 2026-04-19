"""Path-level dataset interface for FLARE-MedFM snapshots."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class FLAREMedFMCase:
    dataset: str
    dataset_dir: str
    case_id: str
    split: str
    modality: str
    image: Path
    label: Path | None = None
    label_type: str = "unlabeled"
    source_root: Path | None = None

    @property
    def has_label(self) -> bool:
        return self.label is not None

    @property
    def complete(self) -> bool:
        return self.image.is_file() and (self.label is None or self.label.is_file())

    def require_complete(self) -> "FLAREMedFMCase":
        missing = [str(self.image)] if not self.image.is_file() else []
        if self.label is not None and not self.label.is_file():
            missing.append(str(self.label))
        if missing:
            key = f"{self.dataset}/{self.case_id}/{self.split}"
            raise FileNotFoundError(f"{key} is incomplete; missing {len(missing)} files: {missing[:3]}")
        return self

    def to_dict(self, relative_to: Path | None = None) -> dict[str, str | int]:
        def fmt(path: Path | None) -> str:
            if path is None:
                return ""
            return str(path.relative_to(relative_to)) if relative_to is not None else str(path)

        return {
            "dataset": self.dataset,
            "dataset_dir": self.dataset_dir,
            "case_id": self.case_id,
            "split": self.split,
            "modality": self.modality,
            "image": fmt(self.image),
            "label": fmt(self.label),
            "has_label": int(self.has_label),
            "label_type": self.label_type,
            "source_root": fmt(self.source_root),
            "complete": int(self.complete),
        }


class FLAREMedFMIndex:
    def __init__(
        self,
        dataset_root: str | Path,
        *,
        manifest_path: str | Path | None = None,
        dataset: str | None = None,
        split: str | None = None,
        modality: str | None = None,
        case_ids: Iterable[str] | None = None,
        labeled_only: bool = False,
        complete_only: bool = False,
    ):
        self.dataset_root = Path(dataset_root).expanduser().resolve()
        self.manifest_path = (
            Path(manifest_path).expanduser().resolve()
            if manifest_path is not None
            else self.dataset_root / "data" / "manifests" / "manifest.csv"
        )
        allowed = set(case_ids) if case_ids is not None else None
        self.records = self._load_manifest(self.manifest_path) if self.manifest_path.is_file() else []
        if dataset is not None:
            self.records = [record for record in self.records if record.dataset == dataset]
        if split is not None:
            self.records = [record for record in self.records if record.split == split]
        if modality is not None:
            self.records = [record for record in self.records if record.modality == modality]
        if allowed is not None:
            self.records = [record for record in self.records if record.case_id in allowed]
        if labeled_only:
            self.records = [record for record in self.records if record.has_label]
        if complete_only:
            self.records = [record for record in self.records if record.complete]
        self.records = sorted(self.records, key=lambda item: (item.dataset, item.split, item.case_id, str(item.image)))
        self._by_key = {(record.dataset, record.case_id, record.split): record for record in self.records}

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self):
        for index in range(len(self)):
            yield self[index]

    def __getitem__(self, index: int) -> FLAREMedFMCase:
        return self.records[index]

    def get(self, dataset: str, case_id: str, split: str = "train") -> FLAREMedFMCase:
        return self._by_key[(dataset, case_id, split)]

    def datasets(self) -> list[str]:
        return sorted({record.dataset for record in self.records})

    def tasks(self) -> list[str]:
        return self.datasets()

    def splits(self) -> list[str]:
        return sorted({record.split for record in self.records})

    def modalities(self) -> list[str]:
        return sorted({record.modality for record in self.records})

    def case_ids(self) -> list[str]:
        return [record.case_id for record in self.records]

    def by_dataset(self, dataset: str) -> list[FLAREMedFMCase]:
        return [record for record in self.records if record.dataset == dataset]

    def by_task(self, task: str) -> list[FLAREMedFMCase]:
        return self.by_dataset(task)

    def by_split(self, split: str) -> list[FLAREMedFMCase]:
        return [record for record in self.records if record.split == split]

    @classmethod
    def from_split(
        cls,
        dataset_root: str | Path,
        split_file: str | Path,
        *,
        manifest_path: str | Path | None = None,
        dataset: str | None = None,
        complete_only: bool = False,
    ) -> "FLAREMedFMIndex":
        case_ids = [
            line.strip().split(",")[0]
            for line in Path(split_file).expanduser().read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        return cls(
            dataset_root,
            manifest_path=manifest_path,
            dataset=dataset,
            case_ids=case_ids,
            complete_only=complete_only,
        )

    def _load_manifest(self, manifest_path: Path) -> list[FLAREMedFMCase]:
        records: list[FLAREMedFMCase] = []
        with manifest_path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                label = self.dataset_root / row["label"] if row.get("label") else None
                source_root = self.dataset_root / row["source_root"] if row.get("source_root") else None
                records.append(
                    FLAREMedFMCase(
                        dataset=row.get("dataset", row.get("task", "")),
                        dataset_dir=row.get("dataset_dir", row.get("task_dir", "")),
                        case_id=row["case_id"],
                        split=row["split"],
                        modality=row.get("modality", ""),
                        image=self.dataset_root / row["image"],
                        label=label,
                        label_type=row.get("label_type", "unlabeled"),
                        source_root=source_root,
                    )
                )
        return records
