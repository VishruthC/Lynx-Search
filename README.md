# 🔥 Custom Semantic Search Engine Sandbox

An end-to-end, open-source vertical web crawler and AI-powered semantic search engine that runs entirely on your local machine. This project bypasses expensive cloud API keys by utilizing a lightweight, open-source embedding model that runs locally on your CPU/GPU.

---

## 🏗️ Architecture Overview

The system is built as a modular data pipeline split into three distinct phases: **Data Ingestion**, **Vector Indexing**, and the **Serving API Layer**.

```
[ Web Pages ] ──→ ( 1. Crawler / BeautifulSoup4 )
                              │
                              ▼
              [ Smart Chunker (600 char blocks) ]
                              │
                              ▼
     ( 2. Local Embedding Model: all-MiniLM-L6-v2 )
                              │
                              ▼
   ( 3. Vector Database / ChromaDB ) ←── [ User Query Via API ]
                              │
                              ▼
   [ UI Search Dashboard / Tailwind ] ──→ [ Sorted Semantic Matches ]
```

---

## 🚀 Features

- **AI-Powered Semantic Retrieval** — Uses local vector embeddings (`all-MiniLM-L6-v2`) to map text into a mathematical vector space, allowing it to understand abstract user intent and contextual meaning rather than relying on strict keyword matching.
- **Targeted Web Crawler** — Automatically traverses domains from a specified seed URL, extracts raw HTML, respects domain boundaries, and sanitizes text by stripping out junk markup, headers, footers, and script tags.
- **Intelligent Text Chunking** — Implements a sliding-window text chunker (600-character limits with a 100-character overlap) to preserve contextual paragraphs and guarantee pinpoint search result granularity.
- **Self-Contained Vector Storage** — Powered by an embedded, serverless instance of ChromaDB that reads and writes straight to your local drive.
- **Modern Web API & UI Dashboard** — Features a clean, single-page search interface styled with Tailwind CSS that communicates seamlessly with a high-performance FastAPI backend server.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Core Language | Python 3.10+ |
| Vector Database | ChromaDB (Persistent Local Client) |
| AI Embedding Pipeline | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| Web Scraping & Parsing | Requests & BeautifulSoup4 |
| Backend API Framework | FastAPI & Uvicorn |
| Frontend Interface | HTML5, Vanilla JavaScript, Tailwind CSS (Play CDN) |

---

## 📂 Project Structure

```text
Lynx-Search/
│
├── documents/            # Optional: Local sandbox .txt files for initial indexing
├── search_index/         # Auto-generated local DB storage (Git ignored)
│
├── app.py                # FastAPI server exposing the search query endpoints
├── crawler.py            # Web crawler, clean text extractor, and semantic chunker
├── engine.py             # Sandbox testing pipeline for local text file parsing
├── index.html            # Minimalist Google-style frontend search UI
│
├── .gitignore            # Excludes caches, DB binaries, and local env files
└── requirements.txt      # Python library dependencies
```

---

## 📦 Installation & Quickstart

### 1. Clone the Repository

```bash
git clone https://github.com/VishruthC/Lynx-Search.git
cd Lynx-Search
```

### 2. Install Dependencies

It is recommended to use a virtual environment before installing packages.

```bash
# Optional: set up a virtual environment
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install required Python modules
pip install -r requirements.txt
```

### 3. Run the Web Crawler

Open `crawler.py` and modify the `TARGET_SITE` URL inside the `__main__` entry point to point to a technical blog or documentation site of your choice, then run:

```bash
python crawler.py
```

> **Note:** On first run, the script will automatically download the ~90MB `all-MiniLM-L6-v2` embedding model from Hugging Face and cache it locally.

### 4. Launch the Search API Server

Start the FastAPI backend via Uvicorn:

```bash
python app.py
```

The server will be live at: `http://127.0.0.1:8000`

### 5. Open the Search Dashboard

Navigate to your project directory and open `index.html` in any web browser. Type a conceptual question — for example, *"How fast do F1 cars go on straights?"* — and watch the system return the best matching text block along with a semantic similarity confidence score.

---

## 🔒 Security & Best Practices

- **Strict Local Persistence** — No web data or proprietary content is ever transmitted to third-party servers or AI vendors; all indexing processes stay entirely on your filesystem.
- **CORS Middleware** — Configured with FastAPI's Cross-Origin Resource Sharing middleware to allow safe communication between the frontend and local API server.
- **Comprehensive `.gitignore`** — Pre-configured to prevent accidental commits of large embedded binary databases or machine-specific Python cache folders (`__pycache__`).

---

## 📄 License

Distributed under the **MIT License**. Feel free to fork it, break it, modify it, or build your own production features on top of it.
