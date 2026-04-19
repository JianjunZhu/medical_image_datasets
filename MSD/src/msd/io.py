"""Optional image loading helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def load_nifti(path: str | Path) -> Any:
    try:
        import nibabel as nib
    except ImportError as exc:
        raise ImportError(
            "load_nifti requires nibabel. Install it with `pip install nibabel`."
        ) from exc
    return nib.load(str(path))
