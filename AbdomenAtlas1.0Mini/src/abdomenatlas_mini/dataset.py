"""Path-level dataset interface for AbdomenAtlas1.0Mini."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .labels import ORGANS


@dataclass(frozen=True)
class CaseRecord:
    case_id: str
    case_dir: Path
    ct: Path
    combined_labels: Path
    segmentations: dict[str, Path]

    @property
    def complete(self) -> bool:
        return (
            self.ct.is_file()
            and self.combined_labels.is_file()
            and all(path.is_file() for path in self.segmentations.values())
        )

    def to_dict(self, relative_to: Path | None = None) -> dict[str, str | int]:
        def format_path(path: Path) -> str:
            if relative_to is not None:
                return str(path.relative_to(relative_to))
            return str(path)

        return {
            "case_id": self.case_id,
            "case_dir": format_path(self.case_dir),
            "ct": format_path(self.ct),
            "combined_labels": format_path(self.combined_labels),
            **{
                f"seg_{organ}": format_path(path)
                for organ, path in self.segmentations.items()
            },
            "complete": int(self.complete),
        }

    def require_complete(self) -> "CaseRecord":
        missing = [
            str(path)
            for path in [self.ct, self.combined_labels, *self.segmentations.values()]
            if not path.is_file()
        ]
        if missing:
            raise FileNotFoundError(
                f"{self.case_id} is incomplete; missing {len(missing)} files: {missing[:3]}"
            )
        return self


class AbdomenAtlasMiniIndex:
    def __init__(
        self,
        dataset_root: str | Path,
        *,
        manifest_path: str | Path | None = None,
        case_ids: Iterable[str] | None = None,
        complete_only: bool = False,
    ):
        self.dataset_root = Path(dataset_root).expanduser().resolve()
        self.raw_dir = self._default_raw_dir()
        self.manifest_path = (
            Path(manifest_path).expanduser().resolve()
            if manifest_path is not None
            else self.dataset_root / "data" / "manifests" / "manifest.csv"
        )
        allowed = set(case_ids) if case_ids is not None else None
        records = (
            self._load_from_manifest(self.manifest_path)
            if self.manifest_path.is_file()
            else self._load_from_dirs()
        )
        if allowed is not None:
            records = [record for record in records if record.case_id in allowed]
        if complete_only:
            records = [record for record in records if record.complete]
        self.records = sorted(records, key=lambda record: record.case_id)
        self._by_case_id = {record.case_id: record for record in self.records}

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self):
        for index in range(len(self)):
            yield self[index]

    def __getitem__(self, index: int) -> CaseRecord:
        return self.records[index]

    def get(self, case_id: str) -> CaseRecord:
        return self._by_case_id[case_id]

    def case_ids(self) -> list[str]:
        return [record.case_id for record in self.records]

    @classmethod
    def from_split(
        cls,
        dataset_root: str | Path,
        split_file: str | Path,
        *,
        manifest_path: str | Path | None = None,
        complete_only: bool = False,
    ) -> "AbdomenAtlasMiniIndex":
        case_ids = [
            line.strip()
            for line in Path(split_file).expanduser().read_text().splitlines()
            if line.strip()
        ]
        return cls(
            dataset_root,
            manifest_path=manifest_path,
            case_ids=case_ids,
            complete_only=complete_only,
        )

    def _load_from_dirs(self) -> list[CaseRecord]:
        return [
            self._record_from_case_dir(case_dir)
            for case_dir in self.raw_dir.glob("BDMAP_*")
            if case_dir.is_dir()
        ]

    def _default_raw_dir(self) -> Path:
        raw_dir = self.dataset_root / "data" / "raw"
        if any(raw_dir.glob("BDMAP_*")):
            return raw_dir
        return self.dataset_root

    def _load_from_manifest(self, manifest_path: Path) -> list[CaseRecord]:
        records: list[CaseRecord] = []
        with manifest_path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                case_dir = self.dataset_root / row["case_dir"]
                records.append(
                    CaseRecord(
                        case_id=row["case_id"],
                        case_dir=case_dir,
                        ct=self.dataset_root / row["ct"],
                        combined_labels=self.dataset_root / row["combined_labels"],
                        segmentations={
                            organ: self.dataset_root / row[f"seg_{organ}"]
                            for organ in ORGANS
                        },
                    )
                )
        return records

    def _record_from_case_dir(self, case_dir: Path) -> CaseRecord:
        return CaseRecord(
            case_id=case_dir.name,
            case_dir=case_dir,
            ct=case_dir / "ct.nii.gz",
            combined_labels=case_dir / "combined_labels.nii.gz",
            segmentations={
                organ: case_dir / "segmentations" / f"{organ}.nii.gz"
                for organ in ORGANS
            },
        )
