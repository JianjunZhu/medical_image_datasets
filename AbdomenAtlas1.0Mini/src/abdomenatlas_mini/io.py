"""Optional image loading helpers.

The core dataset index has no third-party dependencies. These helpers import
`nibabel` only when called.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .dataset import CaseRecord


def load_nifti(path: str | Path) -> Any:
    try:
        import nibabel as nib
    except ImportError as exc:
        raise ImportError(
            "load_nifti requires nibabel. Install it with `pip install nibabel`."
        ) from exc
    return nib.load(str(path))


def load_case_images(case: CaseRecord, *, include_segmentations: bool = True) -> dict[str, Any]:
    images: dict[str, Any] = {
        "ct": load_nifti(case.ct),
        "combined_labels": load_nifti(case.combined_labels),
    }
    if include_segmentations:
        images["segmentations"] = {
            organ: load_nifti(path) for organ, path in case.segmentations.items()
        }
    return images
