# Environment Setup & Tech Stack Specifications

This document outlines the detailed software versions, WSL kernel specs, host requirements, and pre-caching instructions to replicate the **ChillarSeedhi** prototype.

---

## 1. WSL Host Specifications
The prototype was built and verified on the following WSL2 environment:
* **WSL Type:** WSL2 (Standard Microsoft Kernel)
* **Kernel version:** `Linux winpriyanka 6.6.114.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Mon Dec  1 20:46:23 UTC 2025 x86_64 GNU/Linux`
* **Distribution:** `Ubuntu 26.04 LTS (Resolute Raccoon)`
* **Architecture:** `x86_64`

---

## 2. System Level Prerequisites
Ensure the target Ubuntu OS machine has the following packages installed:
* **Python:** `Python 3.12` (Highly stable; matches default package for Ubuntu 24.04/26.04 LTS)
* **NodeJS:** `v24.17.0` (Or standard Node LTS version >= 18)
* **NPM:** `11.13.0`
* **Git** (for version control)

To install on clean Ubuntu:
```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip nodejs npm git
```

---

## 3. Backend Tech Stack (Python 3.12 venv)
Locked package versions in [requirements.txt](file:///home/more/work/ChillarSeedhi/requirements.txt):

| Library Name | Version | Purpose |
| :--- | :--- | :--- |
| `fastapi` | `0.111.0` | Backend API Framework |
| `uvicorn` | `0.30.1` | Asynchronous ASGI Web Server |
| `groq` | `0.9.0` | Groq LPU API client SDK (runs Llama-3.3 and Whisper transcription) |
| `httpx` | `0.27.2` | Async HTTP client (pinned to fix Groq Client compat compatibility) |
| `pydantic` | `2.7.4` | Data schemas & request validation |
| `pydantic-settings` | `2.3.4` | Settings management using env files |
| `python-dotenv` | `1.0.1` | Env loading support |
| `qdrant-client` | `1.9.1` | Qdrant client (configured in-process at `./qdrant_db`) |
| `pymongo` | `4.7.3` | MongoDB connector (optional/production use-case) |
| `langgraph` | `0.1.4` | Multi-agent state orchestration graph |
| `langchain-core` | `0.2.9` | LangGraph core specifications |
| `fastembed` | `0.3.1` | Local semantic embeddings generator |
| `sqlite3` | *Built-in* | Fallback relational/document database storage |

---

## 4. Frontend Tech Stack (React Vite)
Configured dependencies in [frontend/package.json](file:///home/more/work/ChillarSeedhi/frontend/package.json):

| Package Name | Version | Purpose |
| :--- | :--- | :--- |
| `react` | `^19.2.7` | UI render engine |
| `react-dom` | `^19.2.7` | Browser bindings for React |
| `lucide-react` | `^1.21.0` | UI vector icons |
| `recharts` | `^3.9.0` | Dashboard charts & visual gauges |
| `vite` | `^8.1.0` | Build tool and dev server |
| `oxlint` | `^1.69.0` | Linter |

---

## 5. Offline Model Pre-caching (Crucial for Hackathon Environments)
`fastembed` utilizes a local embedding model (`fast-bge-small-en-v1.5`) to vectorise searches in Qdrant. By default, it downloads the model (77.7MB) on its first run and caches it locally.

> [!IMPORTANT]
> If the hackathon machine has **restricted or no internet access**, you must download the cache **before the internet is cut off**. To do so, simply run the seeding script:
> ```bash
> python3 -m backend.rag.seed_kb
> ```
> This downloads and caches the weights inside:
> `~/.cache/fastembed/`
> Ensure this folder exists or is copied alongside your files to run Qdrant 100% offline.
