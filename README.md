<h2 align="center">SurveyX: Academic Survey Automation via Large Language Models</h2>

<p align="center">
  <i>
✨Welcome to SurveyX! If you want to experience the full features, please log in to our website. This open-source code only provides offline processing capabilities.✨
  </i>
  <br>
  <a href="https://arxiv.org/abs/2502.14776">
      <img src="https://img.shields.io/badge/arXiv-Paper-red.svg?logo=arxiv" alt="arxiv paper">
  </a>
  <a href="http://www.surveyx.cn">
    <img src="https://img.shields.io/badge/SurveyX-Web-blue?style=flat" alt="surveyx.cn">
  </a>
  <a href="https://huggingface.co/papers/2502.14776">
    <img src="https://img.shields.io/badge/Huggingface-🤗-yellow?style=flat" alt="huggingface paper">
  </a>
  <a href="https://github.com/IAAR-Shanghai/SurveyX">
    <img src="https://img.shields.io/github/stars/IAAR-Shanghai/SurveyX?style=flat&logo=github&color=yellow" alt="github stars">
  </a>
    <img src="https://img.shields.io/github/last-commit/IAAR-Shanghai/SurveyX?display_timestamp=author&style=flat&color=green" alt="last commit">
  </a>
  <br>
  <a href="https://github.com/IAAR-Shanghai/SurveyX/blob/main/assets/user_groups_123.jpg">
    <img src="https://img.shields.io/badge/Wechat-Group-07c160?style=flat&logo=wechat" alt="Wechat Group">
  </a>
</p>

<div align="center">
    <strong><a>If you find our work helpful, don't forget to give us a star! ⭐️</a></strong>
    <br>
  👉 <strong><a href="https://surveyx.cn/">Visit SurveyX</a></strong> 👈
</div>

\[English | [中文](README_zh.md)\]

## 🤔What is SurveyX?

![surveyx_frame](assets/SurveyX.png)

**SurveyX** is an advanced academic survey automation system that leverages the power of Large Language Models (LLMs) to generate high-quality, domain-specific academic papers and surveys. By simply providing a paper title and keywords for literature retrieval, users can request comprehensive academic papers or surveys tailored to specific topics.

---

## 🆚 Full Version vs. Offline Open Source Version

The open-source code in this repository only provides offline processing capabilities. If you want to experience the full features, please log in to [our website](https://www.surveyx.cn).

**Missing features in the open-source version:**
1. **Real-time online search:** You can only generate surveys based on your own uploaded `.md` format references. The open-source version lacks access to our paper database, web crawler system, keyword expansion algorithms, and dual-layer semantic filtering for literature acquisition.
2. **Multimodal document parsing:** The generated survey will not include image understanding or illustrations from the references.

---

## 🛠️ How to Use the Offline Open Source Version (This repo)

### 1. Prerequisites

- Python 3.11+ (Anaconda recommended)
- All Python dependencies in `requirements.txt`
- LaTeX environment (for PDF compilation):
- You need to convert all your reference documents to Markdown (`.md`) format and put them together in a single folder before running the pipeline.
- PDF text extraction tools (for PDF → MD helper script):
  - Prefer Poppler `pdftotext` (faster, better layout)
    - macOS: `brew install poppler`
    - Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y poppler-utils`
    - Windows (scoop): `scoop install poppler`
  - Fallback library: PyMuPDF (fitz)
    - `pip install pymupdf`

```bash
sudo apt update && sudo apt install texlive-full
```

### 2. Installation

1. Clone the repository:
```bash
git clone https://github.com/IAAR-Shanghai/SurveyX.git
cd SurveyX
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. LLM Configuration

Edit `src/configs/config.py` to provide your LLM API URL, token, and model information before running the pipeline.

Example:
```python
REMOTE_URL = "https://api.openai.com/v1/chat/completions"
TOKEN = "sk-xxxx..."
DEFAULT_EMBED_ONLINE_MODEL = "BAAI/bge-base-en-v1.5"
EMBED_REMOTE_URL = "https://api.siliconflow.cn/v1/embeddings"
EMBED_TOKEN = "your embed token here"
```

### 3.5 PDF → Markdown (Offline References)

Convert your local PDFs to Markdown using Docling, then place all `.md` files in a single folder.

Install and prepare models (recommended, 8GB M1 friendly):
```bash
pip install -U docling docling-tools
docling-tools models download -o "$HOME/.cache/docling/models"
# macOS only, optional but recommended for scanned PDFs
xcode-select --install
pip install -U ocrmac
```

Option A — Formal converter script (recommended):
```bash
bash scripts/docling_pdf_to_md.sh /path/to/pdfs resources/offline_refs/your_topic
```
- macOS (scanned PDFs) with Apple OCR:
  ```bash
  DOC_USE_OCRMAC=1 bash scripts/docling_pdf_to_md.sh /path/to/pdfs resources/offline_refs/your_topic
  ```
- Environment knobs: `DOCLING_ARTIFACTS_PATH` (models cache), `DOC_IMAGE_MODE` (default: placeholder), `DOC_DEVICE` (default: mps on macOS), `DOC_THREADS` (2), `DOC_PAGE_BATCH` (2)

- Note: `--ocr` in Docling is a boolean flag, do not pass `true` as a value. The script handles this for you by adding `--ocr` (and `--ocr-engine ocrmac` if enabled).

Option B — Use the provided test runner:
```bash
bash tests/run_test_docling_to_md.sh [INPUT_PATH] [OUTPUT_DIR]
```
- Defaults: input `resources/offline_refs/pdfs`, output `resources/offline_refs/docling_md_test`
- Uses env `DOCLING_ARTIFACTS_PATH="$HOME/.cache/docling/models"`

Option C — Run Docling manually (recommended flags for 8GB M1):
```bash
docling /path/to/pdfs \
  --to md \
  --image-export-mode placeholder \
  --ocr true --ocr-engine ocrmac --ocr-lang en-US \
  --device mps --num-threads 2 --page-batch-size 2 \
  --output resources/offline_refs/your_topic \
  --artifacts-path "$HOME/.cache/docling/models"
```

Notes:
- Use `--image-export-mode placeholder` to avoid embedding base64 images in Markdown (reduces size and improves downstream processing).
- Keep all `.md` files in a single directory and pass that directory to the offline pipeline.

Validate generated Markdown (optional):
```bash
bash scripts/validate_md_refs.sh resources/offline_refs/your_topic
```

### 4. Workflow


Each run creates a unique result folder under `outputs/`, named by the task id `outputs/<task_id>` (e.g., `outputs/2025-06-18-0935_keyword/`).

Run the full pipeline:
```bash
python tasks/offline_run.py --title "Your Survey Title" --key_words "keyword1, keyword2, ..." --ref_path "path/to/your/reference/dir"
```

Or run step by step:
```bash
export task_id="your_task_id"
python tasks/workflow/03_gen_outlines.py --task_id $task_id
python tasks/workflow/04_gen_content.py --task_id $task_id
python tasks/workflow/05_post_refine.py --task_id $task_id
python tasks/workflow/06_gen_latex.py --task_id $task_id
```

**Note:** Your local reference documents **must be in Markdown (`.md`) format** and placed in a single directory.

### 4. Environment activation convenience

The main scripts (`run.sh`, `scripts/docling_pdf_to_md.sh`, `scripts/download_papers.sh`) will attempt to auto-activate the conda env `surveyx` if available by sourcing `$(conda info --base)/etc/profile.d/conda.sh`. If conda is not installed, they continue without failing. You can always activate manually:

```bash
conda activate surveyx
```

### 5. Output

- All results are saved under `outputs/<task_id>/`
  - `survey.pdf`: Final compiled survey
  - `outlines.json`: Generated outline
  - `latex/`: LaTeX sources
  - `tmp/`: Intermediate files

---

## Example Papers

| Title                                                        | Keywords                                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
|[A Survey of NoSQL Database Systems for Flexible and Scalable Data Management](./examples/Database/A_Survey_of_NoSQL_Database_Systems_for_Flexible_and_Scalable_Data_Management.pdf) | NoSQL, Database Systems, Flexibility, Scalability, Data Management |
|[Vector Databases and Their Role in Modern Data Management and Retrieval A Survey](./examples/Database/Vector_Databases_and_Their_Role_in_Modern_Data_Management_and_Retrieval_A_Survey.pdf) | Vector Databases, Data Management, Data Retrieval, Modern Applications |
|[Graph Databases A Survey on Models, Data Modeling, and Applications](./examples/Database/Graph_Databases_A_Survey_on_Models.pdf) | Graph Databases, Data Modeling |
|[A Survey on Large Language Model Integration with Databases for Enhanced Data Management and Survey Analysis](./examples/Database/A_Survey_on_Large_Language_Model_Integration_with_Databases_for_Enhanced_Data_Management_and_Survey_Analysis.pdf) | Large Language Models, Database Integration, Data Management, Survey Analysis, Enhanced Processing |
|[A Survey of Temporal Databases Real-Time Databases and Data Management Systems](./examples/Database/A_Survey_of_Temporal_Databases_Real.pdf) | Temporal Databases, Real-Time Databases, Data Management |
| [From BERT to GPT-4: A Survey of Architectural Innovations in Pre-trained Language Models](./examples/Computation_and_Language/Transformer.pdf) | Transformer, BERT, GPT-3, self-attention, masked language modeling, cross-lingual transfer, model scaling |
| [Unsupervised Cross-Lingual Word Embedding Alignment: Techniques and Applications](./examples/Computation_and_Language/low.pdf) | low-resource NLP, few-shot learning, data augmentation, unsupervised alignment, synthetic corpora, NLLB, zero-shot transfer |
| [Vision-Language Pre-training: Architectures, Benchmarks, and Emerging Trends](./examples/Computation_and_Language/multimodal.pdf) | multimodal learning, CLIP, Whisper, cross-modal retrieval, modality fusion, video-language models, contrastive learning |
| [Efficient NLP at Scale: A Review of Model Compression Techniques](./examples/Computation_and_Language/model.pdf) | model compression, knowledge distillation, pruning, quantization, TinyBERT, edge computing, latency-accuracy tradeoff |
| [Domain-Specific NLP: Adapting Models for Healthcare, Law, and Finance](./examples/Computation_and_Language/domain.pdf) | domain adaptation, BioBERT, legal NLP, clinical text analysis, privacy-preserving NLP, terminology extraction, few-shot domain transfer |
| [Attention Heads of Large Language Models: A Survey](./examples/Computation_and_Language/attn.pdf) | attention head, attention mechanism, large language model, LLM,transformer architecture, neural networks, natural language processing |
| [Controllable Text Generation for Large Language Models: A Survey](./examples/Computation_and_Language/ctg.pdf) | controlled text generation, text generation, large language model, LLM,natural language processing |
| [A survey on evaluation of large language models](./examples/Computation_and_Language/eval.pdf) | evaluation of large language models,large language models assessment, natural language processing, AI model evaluation |
| [Large language models for generative information extraction: a survey](./examples/Computation_and_Language/infor.pdf) | information extraction, large language models, LLM,natural language processing, generative AI, text mining |
| [Internal consistency and self feedback of LLM](./examples/Computation_and_Language/inter.pdf) | Internal consistency, self feedback, large language model, LLM,natural language processing, model evaluation, AI reliability |
| [Review of Multi Agent Offline Reinforcement Learning](./examples/Computation_and_Language/multi-agent.pdf) | multi agent, offline policy, reinforcement learning,decentralized learning, cooperative agents, policy optimization |
| [Reasoning of large language model: A survey](./examples/Computation_and_Language/reason.pdf) | reasoning of large language models, large language models, LLM,natural language processing, AI reasoning, transformer models |
| [Hierarchy Theorems in Computational Complexity: From Time-Space Tradeoffs to Oracle Separations](examples/Computational_Complexity/P_vs_.pdf) | P vs NP, NP-completeness, polynomial hierarchy, space complexity, oracle separation, Cook-Levin theorem |
| [Classical Simulation of Quantum Circuits: Complexity Barriers and Implications](examples/Computational_Complexity/BQP.pdf) | BQP, quantum supremacy, Shor's algorithm, post-quantum cryptography, QMA, hidden subgroup problem |
| [Kernelization: Theory, Techniques, and Limits](examples/Computational_Complexity/fixed.pdf) | fixed-parameter tractable (FPT), kernelization, treewidth, W-hierarchy, ETH (Exponential Time Hypothesis), parameterized reduction |
| [Optimal Inapproximability Thresholds for Combinatorial Optimization Problems](examples/Computational_Complexity/PCP.pdf) | PCP theorem, approximation ratio, Unique Games Conjecture, APX-hardness, gap-preserving reduction, LP relaxation |
| [Hardness in P: When Polynomial Time is Not Enough](examples/Computational_Complexity/SETH.pdf) | SETH (Strong Exponential Time Hypothesis), 3SUM conjecture, all-pairs shortest paths (APSP), orthogonal vectors problem, fine-grained reduction, dynamic lower bounds |
| [Consistency Models in Distributed Databases: From ACID to NewSQL](examples/Database/CAP.pdf) | CAP theorem, ACID vs BASE, Paxos/Raft, Spanner, NewSQL, sharding, linearizability |
| [Cloud-Native Databases: Architectures, Challenges, and Future Directions](examples/Database/CAP.pdf) | cloud databases, AWS Aurora, Snowflake, storage-compute separation, auto-scaling, pay-per-query, multi-tenancy |
| [Graph Database Systems: Storage Engines and Query Optimization Techniques](examples/Database/graph.pdf) | graph traversal, Neo4j, SPARQL, property graph, subgraph matching, RDF triplestore, Gremlin |
| [Real-Time Aggregation in TSDBs: Techniques for High-Cardinality Data](examples/Database/time.pdf) | time-series data, InfluxDB, Prometheus, downsampling, time windowing, high-cardinality indexing, stream processing |
| [Self-Driving Databases: A Survey of AI-Powered Autonomous Management](examples/Database/auto.pdf) | autonomous databases, learned indexes, query optimization, Oracle AutoML, workload forecasting, anomaly detection |
| [Multi-Model Databases: Integrating Relational, Document, and Graph Paradigms](examples/Database/mmd.pdf) | multi-model database, MongoDB, ArangoDB, JSONB, unified query language, schema flexibility, polystore |
| [Vector Databases for AI: Efficient Similarity Search and Retrieval-Augmented Generation](examples/Networking_and_Internet_Architecture/vector.pdf) | vector database, FAISS, Milvus, ANN search, embedding indexing, RAG (Retrieval-Augmented Generation), HNSW |
| [Software-Defined Networking: Evolution, Challenges, and Future Scalability](examples/Networking_and_Internet_Architecture/open.pdf) | OpenFlow, control plane/data plane separation, NFV orchestration, network slicing, P4 language, OpenDaylight, scalability bottlenecks |
| [Beyond 5G: Architectural Innovations for Terahertz Communication and Network Slicing](examples/Networking_and_Internet_Architecture/network.pdf) | network slicing, MEC (Multi-access Edge Computing), beamforming, mmWave, URLLC (Ultra-Reliable Low-Latency Communication), O-RAN, energy efficiency |
| [IoT Network Protocols: A Comparative Study of LoRaWAN, NB-IoT, and Thread](examples/Networking_and_Internet_Architecture/LPWAN.pdf) | LPWAN, LoRa, ZigBee 3.0, 6LoWPAN, TDMA scheduling, RPL routing, device density management |
| [Edge Caching in Content Delivery Networks: Algorithms and Economic Incentives](examples/Networking_and_Internet_Architecture/CDN.pdf) | CDN, Akamai, cache replacement policies, DASH (Dynamic Adaptive Streaming), QoE optimization, edge server placement, bandwidth cost reduction |
| [A survey on  flow batteries](examples/Other/battery.pdf)    | battery electrolyte formulation                              |
| [Research on battery electrolyte formulation](examples/Other/flow_battery.pdf) | flow batteries                                               |

## 📃Citing SurveyX

Please cite us if you find this project helpful for your project/paper:

```plain text
@misc{liang2025surveyxacademicsurveyautomation,
      title={SurveyX: Academic Survey Automation via Large Language Models}, 
      author={Xun Liang and Jiawei Yang and Yezhaohui Wang and Chen Tang and Zifan Zheng and Shichao Song and Zehao Lin and Yebin Yang and Simin Niu and Hanyu Wang and Bo Tang and Feiyu Xiong and Keming Mao and Zhiyu li},
      year={2025},
      eprint={2502.14776},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2502.14776}, 
}
```

<hr style="border: 1px solid #ecf0f1;">


## Open Source Version Notice
This open source version of Surveyx is a simplified edition. It relies entirely on user-provided local reference documents and does not include advanced features such as:
- Keyword expansion and filtering algorithms
- Multimodal image parsing or figure extraction
- Online reference search or automatic data fetching
### 3.6 Download PDFs from a curated JSON list

If you have a curated list such as `resources/included_papers_20250825_balanced.json`, you can batch download the PDFs:

```bash
# Python script
python scripts/download_papers.py \
  --json resources/included_papers_20250825_balanced.json \
  --out-dir datasets/papers \
  --concurrency 6

# Or via run.sh
./run.sh download resources/included_papers_20250825_balanced.json datasets/papers -- --concurrency 6
```

Details:
- Defaults to downloading only entries with `is_included: true`. Use `--all` to download all.
- Outputs to `datasets/papers` by default, writes a manifest `download_manifest.jsonl`, and logs failures to `download_failures.txt`.
- Filenames use `id - title.pdf` with illegal characters sanitized.

These advanced modules are only available in the full version of Surveyx, which is hosted by MemTensor (Shanghai) Technology Co., Ltd. If you would like to experience the complete features, please visit our official website: [surveyx.cn](https://surveyx.cn)

---

## 🧪 Sandbox - AI Agent Practice Environment

The `sandbox/` directory contains practice scenarios for AI agents to learn debugging and problem-solving:

- **`latex_citation_fix/`** - LaTeX compilation errors and citation escaping issues (Difficulty: ⭐⭐⭐⭐)

Each sandbox provides:
- Original problematic files
- Verification scripts
- Reset tools
- Reference solutions (optional)

See `sandbox/README.md` for details.

---

For questions or issues, please open an issue on the repository.

## ⚠️ Disclaimer

SurveyX uses advanced language models to assist with the generation of academic papers. However, it is important to note that the generated content is a tool for research assistance. Users should verify the accuracy of the generated papers, as SurveyX cannot guarantee full compliance with academic standards.
