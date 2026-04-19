"""PyTorch- and MONAI-friendly adapters for FLARE-MedFM."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable

from .dataset import FLAREMedFMCase, FLAREMedFMIndex


class FLAREMedFMTorchDataset:
    """Map-style dataset compatible with PyTorch DataLoader without importing torch."""

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
        complete_only: bool = True,
        transform: Callable[[dict[str, Any]], Any] | None = None,
        load_images: bool = False,
        include_metadata: bool = True,
    ):
        self.index = FLAREMedFMIndex(
            dataset_root,
            manifest_path=manifest_path,
            dataset=dataset,
            split=split,
            modality=modality,
            case_ids=case_ids,
            labeled_only=labeled_only,
            complete_only=complete_only,
        )
        self.transform = transform
        self.load_images = load_images
        self.include_metadata = include_metadata

    def __len__(self) -> int:
        return len(self.index)

    def __getitem__(self, index: int) -> Any:
        sample = self.sample_from_case(self.index[index])
        if self.transform is not None:
            return self.transform(sample)
        return sample

    def sample_from_case(self, record: FLAREMedFMCase) -> dict[str, Any]:
        record.require_complete()
        sample: dict[str, Any] = {
            "image": str(record.image),
            "label": str(record.label) if record.label is not None else None,
            "dataset": record.dataset,
            "case_id": record.case_id,
            "split": record.split,
            "modality": record.modality,
        }
        if self.include_metadata:
            sample.update(
                {
                    "image_path": str(record.image),
                    "label_path": str(record.label) if record.label is not None else "",
                    "label_type": record.label_type,
                    "dataset_dir": record.dataset_dir,
                    "source_root": str(record.source_root) if record.source_root is not None else "",
                }
            )
        if self.load_images:
            from .io import load_nifti

            sample["image_nii"] = load_nifti(record.image)
            if record.label is not None:
                sample["label_nii"] = load_nifti(record.label)
        return sample

    def as_monai_data(self) -> list[dict[str, Any]]:
        return [self.sample_from_case(record) for record in self.index]


def build_monai_dataset(
    dataset_root: str | Path,
    *,
    transform: Callable[[dict[str, Any]], Any] | None = None,
    manifest_path: str | Path | None = None,
    dataset: str | None = None,
    split: str | None = None,
    modality: str | None = None,
    case_ids: Iterable[str] | None = None,
    labeled_only: bool = False,
    complete_only: bool = True,
    dataset_cls: type | None = None,
    **dataset_kwargs: Any,
) -> Any:
    adapter = FLAREMedFMTorchDataset(
        dataset_root,
        manifest_path=manifest_path,
        dataset=dataset,
        split=split,
        modality=modality,
        case_ids=case_ids,
        labeled_only=labeled_only,
        complete_only=complete_only,
        transform=None,
        load_images=False,
        include_metadata=True,
    )
    data = adapter.as_monai_data()
    if dataset_cls is None:
        try:
            from monai.data import Dataset as dataset_cls
        except ImportError as exc:
            raise ImportError(
                "build_monai_dataset requires MONAI. Install it with `pip install monai`."
            ) from exc
    return dataset_cls(data=data, transform=transform, **dataset_kwargs)
