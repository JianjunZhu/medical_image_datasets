# Labels

The dataset contains individual segmentation masks for:

- `aorta`
- `gall_bladder`
- `kidney_left`
- `kidney_right`
- `liver`
- `pancreas`
- `postcava`
- `spleen`
- `stomach`

Each case also includes `combined_labels.nii.gz`. Confirm numeric label IDs from
the official dataset documentation or direct image inspection before training
code assumes a mapping.
