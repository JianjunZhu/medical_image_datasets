"""PyTorch- and MONAI-friendly dataset adapters for MSD."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable

from .dataset import MSDCase, MSDIndex


class MSDTorchDataset:
    """A lightweight map-style dataset compatible with PyTorch DataLoader.

    The class does not inherit from ``torch.utils.data.Dataset`` so importing
    it does not require PyTorch. PyTorch DataLoader only requires ``__len__``
    and ``__getitem__`` for map-style datasets.
    """

    def __init__(
        self,
        dataset_root: str | Path,
        *,
        manifest_path: str | Path | None = None,
        task: str | None = None,
        split: str | None = None,
        case_ids: Iterable[str] | None = None,
        complete_only: bool = True,
        transform: Callable[[dict[str, Any]], Any] | None = None,
        load_images: bool = False,
        include_metadata: bool = True,
    ):
        self.index = MSDIndex(
            dataset_root,
            manifest_path=manifest_path,
            task=task,
            split=split,
            case_ids=case_ids,
            complete_only=complete_only,
        )
        self.dataset_root = self.index.dataset_root
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

    def sample_from_case(self, record: MSDCase) -> dict[str, Any]:
        record.require_complete()
        sample: dict[str, Any] = {
            "image": str(record.image),
            "label": str(record.label) if record.label is not None else None,
            "task_name": record.task_name,
            "case_id": record.case_id,
            "split": record.split,
        }
        if self.include_metadata:
            sample.update(
                {
                    "image_path": str(record.image),
                    "label_path": str(record.label) if record.label is not None else "",
                    "task_dir": str(record.task_dir) if record.task_dir is not None else "",
                    "dataset_json": str(record.dataset_json) if record.dataset_json is not None else "",
                }
            )
        if self.load_images:
            from .io import load_nifti

            sample["image_nii"] = load_nifti(record.image)
            if record.label is not None:
                sample["label_nii"] = load_nifti(record.label)
        return sample

    def as_monai_data(self) -> list[dict[str, Any]]:
        """Return MONAI-style dictionaries with image and label path keys."""
        return [self.sample_from_case(record) for record in self.index]


def build_monai_dataset(
    dataset_root: str | Path,
    *,
    transform: Callable[[dict[str, Any]], Any] | None = None,
    manifest_path: str | Path | None = None,
    task: str | None = None,
    split: str | None = None,
    case_ids: Iterable[str] | None = None,
    complete_only: bool = True,
    dataset_cls: type | None = None,
    **dataset_kwargs: Any,
) -> Any:
    """Build a MONAI Dataset from MSD path dictionaries.

    MONAI is imported only when this function is called. Pass ``dataset_cls``
    to use alternatives such as ``monai.data.CacheDataset``.
    """
    adapter = MSDTorchDataset(
        dataset_root,
        manifest_path=manifest_path,
        task=task,
        split=split,
        case_ids=case_ids,
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
