# Source

The source of truth for this workspace is the FLARE-MedFM Hugging Face
organization:

- <https://huggingface.co/FLARE-MedFM>
- Project homepage: <https://flare-medfm.github.io/>

The organization currently exposes 10 datasets:

| Key | Repository | License |
| --- | --- | --- |
| `pancancer_ct_seg` | `FLARE-MedFM/PancancerCTSeg` | CC-BY-NC-4.0 |
| `task2_laptop_seg` | `FLARE-MedFM/FLARE-Task2-LaptopSeg` | CC-BY-NC-4.0 |
| `task3_domain_adaptation` | `FLARE-MedFM/FLARE-Task3-DomainAdaption` | CC-BY-NC-4.0 |
| `task4_ct_fm` | `FLARE-MedFM/FLARE-Task4-CT-FM` | CC-BY-NC-4.0 |
| `task4_mri_fm` | `FLARE-MedFM/FLARE-Task4-MRI-FM` | CC-BY-NC-4.0 |
| `flare26_mllm_3d` | `FLARE-MedFM/FLARE26-MLLM-3D` | CC-BY-NC-4.0 |
| `task5_mllm_2d` | `FLARE-MedFM/FLARE-Task5-MLLM-2D` | CC-BY-NC-4.0 |
| `task6_medagent` | `FLARE-MedFM/FLARE-Task6-MedAgent` | CC-BY-NC-4.0 |
| `task1_recist_to_3d` | `FLARE-MedFM/FLARE-Task1-PancancerRECIST-to-3D` | CC-BY-NC-SA-4.0 |
| `task1_recist_to_3d_dockers` | `FLARE-MedFM/FLARE-Task1-PancancerRECIST-to-3D-Dockers` | unknown |

Most repositories are gated. Participants must log in to Hugging Face and
accept the dataset access conditions before downloading files. Store local
credentials in `secrets/hf_token` or pass `HF_TOKEN`; never commit tokens.
