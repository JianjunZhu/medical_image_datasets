"""Image I/O helpers for FLARE24."""

from __future__ import annotations

from pathlib import Path


def load_nifti(path: str | Path):
    """Load a NIfTI image with nibabel.

    nibabel is imported lazily so path indexing works without imaging
    dependencies installed.
    """
    try:
        import nibabel as nib
    except ImportError as exc:
        raise ImportError("load_nifti requires nibabel. Install it with `pip install nibabel`.") from exc
    return nib.load(str(path))
