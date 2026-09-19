# YarnRAG

YarnRAG is an experimental conversational RAG prototype for exploring Nigerian public discourse. It transforms retrieved Nairaland conversations into grounded, context-aware answers that reflect the viewpoints, debates, humour, and lived experiences expressed in the discussions.

Built with retrieval-augmented generation (RAG), YarnRAG retrieves relevant discussions instead of relying on generic model knowledge. It is designed to show what people actually said, where opinions diverged, and where the retrieved conversations do not provide enough information.

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Chroma](https://img.shields.io/badge/Chroma-Vector%20Database-FE4A49)](https://www.trychroma.com/)
[![Hugging%20Face](https://img.shields.io/badge/Hugging%20Face-Models-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


> **Current status:** experimental RAG project. The scraping scripts can run locally; the cleaning and RAG workflows currently live in Google Colab notebooks.

---

## Tech stack

| Area | Technology |
| --- | --- |
| Language and environment | Python 3.12, uv, Google Colab |
| Data collection | Requests, Beautiful Soup, pandas |
| Data preparation | Python standard libraries, pandas, Jupyter notebooks |
| RAG orchestration | LangChain with multi-query expansion for query transformation |
| Embeddings | `BAAI/bge-small-en-v1.5` via Hugging Face |
| Vector database | Chroma |
| Answer-generation model | Hugging Face Inference Endpoint with Qwen/Qwen3-4B-Instruct-2507 |

---

## What it does

1. Finds discussion-thread links from selected Nairaland categories.
2. Scrapes each thread's main post and comments into JSON Lines data.
3. Cleans discussion text, removes common spam and contact details, and reduces duplicated quoted replies.
4. Builds a balanced cleaned subset across six categories.
5. Chunks and embeds discussions into a persistent Chroma vector store.
6. Retrieves relevant discussions for a question and asks an LLM to produce a grounded, conversational answer.

---

## Data coverage

The checked-in cleaned dataset contains 600 discussion threads: 100 each from:

- Politics
- Education
- Sports
- Jokes
- Romance
- Tech

All data is sourced from public Nairaland pages. Discussion content may contain opinions, inaccurate claims, offensive language, or personal information posted by forum users. It should not be treated as verified news or professional advice.

---

## Project structure

```text
YarnRAG/
├── data/
│   ├── raw_data/
│   │   ├── thread_links.csv        # Discovered thread URLs and categories
│   │   └── thread_data.jsonl       # Scraped main posts and comments
│   └── cleaned_data/
│       └── cleaned_threads.json    # Prepared RAG documents
├── notebooks/
│   ├── threads_cleaning.ipynb      # Cleaning and dataset balancing workflow
│   └── rag.ipynb                   # Embedding, retrieval, and answer generation
├── scraper/
│   ├── discover_threads.py         # Finds thread links by category
│   └── scrape_threads.py           # Fetches and extracts thread content
├── pyproject.toml
└── README.md
```

---

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A Google Colab environment for the current notebooks
- A Hugging Face API token for the LLM step in `notebooks/rag.ipynb`

Install the local scraping dependencies with uv:

```bash
uv sync
```

Or, with pip:

```bash
pip install beautifulsoup4 fake-useragent pandas requests
```

---

## Collecting data

The scraper uses `requests` and Beautiful Soup. It includes delays between requests; please keep the rate conservative and respect Nairaland's terms, robots policy, and any access restrictions.

### 1. Discover thread links

```bash
uv run python scraper/discover_threads.py
```

This visits the configured category pages and writes discovered links to:

```text
data/raw_data/thread_links.csv
```

The categories and number of pages are configured near the top of `scraper/discover_threads.py`.

### 2. Scrape thread posts and comments

```bash
uv run python scraper/scrape_threads.py
```

This reads `thread_links.csv` and appends one JSON object per successfully extracted thread to:

```text
data/raw_data/thread_data.jsonl
```

Because output is appended, back up or remove/rename the existing JSONL file before a fresh full scrape if duplicate records are not wanted.

---

## Cleaning the data

Open `notebooks/threads_cleaning.ipynb` in Google Colab. The notebook currently:

- normalizes Unicode and whitespace;
- removes simple HTML artifacts;
- replaces URLs, email addresses, and Nigerian phone numbers with placeholders;
- filters very short and obvious spam comments;
- identifies some repeated quoted comments; and
- selects up to 100 threads from each configured category.

Update the notebook's Google Drive input and output paths before running it. Its output is `cleaned_threads.json`.

---

## Building and querying the RAG system

Open `notebooks/rag.ipynb` in Google Colab.

The notebook:

1. Loads `cleaned_threads.json`.
2. Converts each thread to a LangChain `Document`.
3. Splits documents into overlapping token-aware chunks.
4. Embeds chunks with `BAAI/bge-small-en-v1.5`.
5. Persists or loads a Chroma vector store from Google Drive.
6. Uses multi-query retrieval to find relevant discussion chunks.
7. Sends the retrieved context to a Hugging Face-hosted Qwen model for an answer.

The notebook installs its own RAG dependencies in Colab. Set the `HF_INFERENCE_TOKEN` secret in Colab before running the LLM cells, and change the Drive paths if needed.

---

## Grounded-answering principles

YarnRAG represents retrieved discussions, not forum opinion as fact. Its answers:

- rely only on retrieved evidence and attribute viewpoints carefully;
- reflect relevant conversational context and disagreement;
- answer the question directly, using quotes sparingly; and
- respond with `I don't know.` when evidence is insufficient.

---

## License

This project is released under the [MIT License](LICENSE).
