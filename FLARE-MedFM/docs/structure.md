# Structure

The project keeps source snapshots and derived indexes separate:

```text
FLARE-MedFM/
  data/
    raw/
      huggingface/
        PancancerCTSeg/
        FLARE-Task2-LaptopSeg/
        FLARE-Task3-DomainAdaption/
        FLARE-Task4-CT-FM/
        FLARE-Task4-MRI-FM/
        FLARE26-MLLM-3D/
        FLARE-Task5-MLLM-2D/
        FLARE-Task6-MedAgent/
        FLARE-Task1-PancancerRECIST-to-3D/
        FLARE-Task1-PancancerRECIST-to-3D-Dockers/
      extracted/
    processed/
    manifests/
    splits/
```

Some repositories contain nested `.zip` or `.7z` files. Keep the original
snapshot under `data/raw/huggingface/` and unpack copies into
`data/raw/extracted/`.
