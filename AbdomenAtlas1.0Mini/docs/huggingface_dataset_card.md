---
license: cc-by-nc-sa-4.0
task_categories:
- image-segmentation
tags:
- medical
pretty_name: AbdomenAtlas 1.0 Mini
size_categories:
- 1K<n<10K
extra_gated_prompt: >
  ## Terms and Conditions for Using the AbdomenAtlas 1.0 Mini Dataset


  **1. Acceptance of Terms**

  Accessing and using the AbdomenAtlas 1.0 Mini dataset implies your agreement
  to these terms and conditions. If you disagree with any part, please refrain
  from using the dataset.


  **2. Permitted Use**

  - The dataset is intended solely for academic, research, and educational
  purposes.

  - Any commercial exploitation of the dataset without prior permission is
  strictly forbidden.

  - You must adhere to all relevant laws, regulations, and research ethics,
  including data privacy and protection standards.


  **3. Data Protection and Privacy**

  - Acknowledge the presence of sensitive information within the dataset and
  commit to maintaining data confidentiality.

  - Direct attempts to re-identify individuals from the dataset are prohibited.

  - Ensure compliance with data protection laws such as GDPR and HIPAA.


  **4. Attribution**

  - Cite the dataset and acknowledge the providers in any publications resulting
  from its use.

  - Claims of ownership or exclusive rights over the dataset or derivatives are
  not permitted.


  **5. Redistribution**

  - Redistribution of the dataset or any portion thereof is not allowed.

  - Sharing derived data must respect the privacy and confidentiality terms set
  forth.


  **6. Disclaimer**

  The dataset is provided "as is" without warranty of any kind, either expressed
  or implied, including but not limited to the accuracy or completeness of the
  data.


  **7. Limitation of Liability**

  Under no circumstances will the dataset providers be liable for any claims or
  damages resulting from your use of the dataset.


  **8. Access Revocation**

  Violation of these terms may result in the termination of your access to the
  dataset.


  **9. Amendments**

  The terms and conditions may be updated at any time; continued use of the
  dataset signifies acceptance of the new terms.


  **10. Governing Law**

  These terms are governed by the laws of the location of the dataset providers,
  excluding conflict of law rules.


  **Consent:**

  Accessing and using the AbdomenAtlas 1.0 Mini dataset signifies your
  acknowledgment and agreement to these terms and conditions.
extra_gated_fields:
  Name: text
  Institution: text
  Email: text
  I have read and agree with Terms and Conditions for using the dataset: checkbox
---

# Dataset Summary

One of the largest, fully-annotated CT dataset to date, including **5,195 annotated CT volumes** (with spleen, liver, kidneys, stomach, 
gallbladder, pancreas, aorta, and IVC annotations).

---

# Submit your Checkpoint for External Evaluation and Join the Touchstone Benchmarking Project! 

The Benchmarking Project aims to compare diverse semantic segmentation algorithms. 
We, the CCVL research group at Johns Hopkins University, invite you to contribute to this initiative. 
Train your AI algorithm using AbomenAtlas1.0 (and/or other datasets) and send us your trained checkpoint
along with basic information about your model, such as the names of its training datasets. 
**We will evaluate your checkpoint on JHH**, a large private dataset at Johns Hopkins University. 
Our **external evaluation** is being conducted on an **unprecedented scale**: 
JHH comprises more than **5,000 CT volumes**, originating from a hospital that is **absent from any public 
dataset**. 
This allows us to evaluate neural networks in an unseen clinical environment. 
To increase data diversity in evaluation, we will also test your model on public datasets from diverse contries. 
Afterward, we will send you your model's performance, and we will invite you to include 
it in our future online leaderboard.

Please **email** psalvad2@jh.edu for information on how to prepare and submit your checkpoint and for
opportunities to collaborate in our future publications!

---

# Dataset variants:

[AbdomenAtlas1.0Mini](https://huggingface.co/datasets/AbdomenAtlas/AbdomenAtlas1.0Mini) - 5,195 annotated CT volumes, improved label quality for aorta and kidneys

[_AbdomenAtlas1.0Mini](https://huggingface.co/datasets/AbdomenAtlas/_AbdomenAtlas1.0Mini) - same as above, but structured as large zip files, to facilitate downloading

[AbdomenAtlas1.0MiniBeta](https://huggingface.co/datasets/AbdomenAtlas/AbdomenAtlas1.0MiniBeta) - 5,195 annotated CT volumes, with noisy labels for aorta and kidneys

---

# Downloading Instructions

#### 1- Register at Huggingface, accept our terms and conditions, and create an access token:

[Create a Huggingface account](https://huggingface.co/join)

[Log in](https://huggingface.co/login)

[Accept our terms and conditions for acessing this dataset](https://huggingface.co/datasets/AbdomenAtlas/AbdomenAtlas1.0Mini) (top of this page)

[Create a Huggingface access token](https://huggingface.co/settings/tokens) and copy it (you will use it in step 3, in paste_your_token_here)


#### 2- Install the Hugging Face library:
```bash
pip install huggingface_hub[hf_transfer]==0.24.0
HF_HUB_ENABLE_HF_TRANSFER=1
```
<details>
<summary style="margin-left: 25px;">[Optional] Alternative without HF Trasnsfer (slower)</summary>
<div style="margin-left: 25px;">
  
```bash
pip install huggingface_hub==0.24.0
```

</div>
</details>

#### 3- Download the dataset:
```bash
mkdir AbdomenAtlas
cd AbdomenAtlas
huggingface-cli download AbdomenAtlas/AbdomenAtlas1.0Mini --token paste_your_token_here --repo-type dataset --local-dir .
```

<details>
<summary style="margin-left: 25px;">[Optional] Resume downloading</summary>
<div style="margin-left: 25px;">

In case you had a previous interrupted download, just run the huggingface-cli download command above again.
```bash
huggingface-cli download AbdomenAtlas/AbdomenAtlas1.0Mini --token paste_your_token_here --repo-type dataset --local-dir .
```
</div>
</details>

## Paper

<b>AbdomenAtlas-8K: Annotating 8,000 CT Volumes for Multi-Organ Segmentation in Three Weeks</b> <br/>
[Chongyu Qu](https://github.com/Chongyu1117)<sup>1</sup>, [Tiezheng Zhang](https://github.com/ollie-ztz)<sup>1</sup>, [Hualin Qiao](https://www.linkedin.com/in/hualin-qiao-a29438210/)<sup>2</sup>, [Jie Liu](https://ljwztc.github.io/)<sup>3</sup>, [Yucheng Tang](https://scholar.google.com/citations?hl=en&user=0xheliUAAAAJ)<sup>4</sup>, [Alan L. Yuille](https://www.cs.jhu.edu/~ayuille/)<sup>1</sup>, and [Zongwei Zhou](https://www.zongweiz.com/)<sup>1,*</sup> <br/>
<sup>1 </sup>Johns Hopkins University,  <br/>
<sup>2 </sup>Rutgers University,  <br/>
<sup>3 </sup>City University of Hong Kong,   <br/>
<sup>4 </sup>NVIDIA <br/>
NeurIPS 2023 <br/>
[paper](https://www.cs.jhu.edu/~alanlab/Pubs23/qu2023abdomenatlas.pdf) | [code](https://github.com/MrGiovanni/AbdomenAtlas) | [dataset](https://huggingface.co/datasets/AbdomenAtlas/AbdomenAtlas1.0Mini) | [annotation](https://www.dropbox.com/scl/fi/28l5vpxrn212r2ejk32xv/AbdomenAtlas.tar.gz?rlkey=vgqmao4tgv51hv5ew24xx4xpm&dl=0) | [poster](document/neurips_poster.pdf)

<b>How Well Do Supervised 3D Models Transfer to Medical Imaging Tasks?</b> <br/>
[Wenxuan Li](https://scholar.google.com/citations?hl=en&user=tpNZM2YAAAAJ), [Alan Yuille](https://www.cs.jhu.edu/~ayuille/), and [Zongwei Zhou](https://www.zongweiz.com/)<sup>*</sup> <br/>
Johns Hopkins University  <br/>
International Conference on Learning Representations (ICLR) 2024 (oral; top 1.2%) <br/>
[paper](https://www.cs.jhu.edu/~alanlab/Pubs23/li2023suprem.pdf) | [code](https://github.com/MrGiovanni/SuPreM) 

## Citation 

```
@article{li2024abdomenatlas,
  title={AbdomenAtlas: A large-scale, detailed-annotated, \& multi-center dataset for efficient transfer learning and open algorithmic benchmarking},
  author={Li, Wenxuan and Qu, Chongyu and Chen, Xiaoxi and Bassi, Pedro RAS and Shi, Yijia and Lai, Yuxiang and Yu, Qian and Xue, Huimin and Chen, Yixiong and Lin, Xiaorui and others},
  journal={Medical Image Analysis},
  pages={103285},
  year={2024},
  publisher={Elsevier},
  url={https://github.com/MrGiovanni/AbdomenAtlas}
}

@article{bassi2024touchstone,
  title={Touchstone Benchmark: Are We on the Right Way for Evaluating AI Algorithms for Medical Segmentation?},
  author={Bassi, Pedro RAS and Li, Wenxuan and Tang, Yucheng and Isensee, Fabian and Wang, Zifu and Chen, Jieneng and Chou, Yu-Cheng and Kirchhoff, Yannick and Rokuss, Maximilian and Huang, Ziyan and others},
  journal={arXiv preprint arXiv:2411.03670},
  year={2024}
}

@inproceedings{li2024well,
  title={How Well Do Supervised Models Transfer to 3D Image Segmentation?},
  author={Li, Wenxuan and Yuille, Alan and Zhou, Zongwei},
  booktitle={The Twelfth International Conference on Learning Representations},
  year={2024}
}

@article{qu2023abdomenatlas,
  title={Abdomenatlas-8k: Annotating 8,000 CT volumes for multi-organ segmentation in three weeks},
  author={Qu, Chongyu and Zhang, Tiezheng and Qiao, Hualin and Tang, Yucheng and Yuille, Alan L and Zhou, Zongwei},
  journal={Advances in Neural Information Processing Systems},
  volume={36},
  year={2023}
}


```

## Acknowledgements
This work was supported by the Lustgarten Foundation for Pancreatic Cancer Research and partially by the Patrick J. McGovern Foundation Award. We appreciate the effort of the MONAI Team to provide open-source code for the community.

## License
AbdomenAtlas 1.0</a> is licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">CC BY-NC-SA 4.0.</a></p>

## Uploading AbdomenAtlas to HuggingFace
The file AbdomenAtlasUploadMultipleFolders.ipynb has the code we used to upload AbdomenAtlas to Hugging Face. It may be ncessary to run the script multiple times, until it finishes without an uploading error. The uploading script requires PyTorch, huggingface_hub, and Jupyter Notebook.