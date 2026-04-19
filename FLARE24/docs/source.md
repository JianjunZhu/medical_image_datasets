# Source

FLARE24 task metadata is tracked from the official challenge pages and the
FLARE-MedFM Hugging Face dataset cards.

## Official Pages

- Homepage: <https://flare-medfm.github.io/>
- Task 1 CodaBench: <https://www.codabench.org/competitions/2319/>
- Task 2 CodaBench: <https://www.codabench.org/competitions/2320/>
- Task 3 CodaBench: <https://www.codabench.org/competitions/2296/>
- FLARE-MedFM Hugging Face organization: <https://huggingface.co/FLARE-MedFM>

The CodaBench pages are JavaScript-rendered in static fetches; use them as the
challenge authority. The downloadable data descriptions are mirrored in the
Hugging Face dataset cards listed below.

## Dataset Repositories

| Task | Repository | Access | License |
| --- | --- | --- | --- |
| Task 1 | `FLARE-MedFM/FLARE-Task1-Pancancer` | gated | CC-BY-NC-4.0 |
| Task 2 | `FLARE-MedFM/FLARE-Task2-LaptopSeg` | gated | CC-BY-NC-4.0 |
| Task 3 | `FLARE-MedFM/FLARE-Task3-DomainAdaption` | gated | CC-BY-NC-4.0 |

Participants must log in to Hugging Face and accept the dataset access
conditions before downloading files. Store local credentials in `secrets/hf_token`
or pass `HF_TOKEN`; never commit tokens.
