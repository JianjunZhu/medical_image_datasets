# Structure

The project keeps source snapshots and derived indexes separate:

```text
FLARE24/
  data/
    raw/
      huggingface/
        FLARE-Task1-Pancancer/
        FLARE-Task2-LaptopSeg/
        FLARE-Task3-DomainAdaption/
      extracted/
    processed/
    manifests/
    splits/
```

Expected upstream task structures:

```text
FLARE-Task1-Pancancer/
  train_label/
  train_unlabel/
  validation/

FLARE-Task2-LaptopSeg/
  coreset_train_50_random/
  train_gt_label/
  train_pseudo_label/
  validation/

FLARE-Task3-DomainAdaption/
  coreset_train_unlabeled_MRI_PET/
  train_CT_gt_label/
  train_CT_pseudolabel/
  train_MRI_unlabeled/
  train_PET_unlabeled/
  validation/
```

Some labels are distributed as `.zip` or `.7z` files inside the Hugging Face
snapshot. Keep the original archives in `data/raw/huggingface/` and unpack
copies into `data/raw/extracted/`.
