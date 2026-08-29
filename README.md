# ✈️ AeroIntel AI
### Intelligent Aviation Investigation Report Analysis using RAG, LangGraph & Knowledge Graph

![Python](https://img.shields.io/badge/Python-3.10-blue)
![LangChain](https://img.shields.io/badge/LangChain-RAG-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-orange)
![FAISS](https://img.shields.io/badge/VectorDB-FAISS-red)
![Neo4j](https://img.shields.io/badge/KnowledgeGraph-Neo4j-blue)
![Groq](https://img.shields.io/badge/LLM-Groq-purple)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

---

## 📖 Overview

**AeroIntel AI** is an AI powered Document Intelligence platform designed for aviation investigation reports.

The system combines:

- 📚 Retrieval Augmented Generation (RAG)
- 🧠 LangGraph Agentic Workflow
- 🔎 Hybrid Retrieval
- 🗂 Metadata Search
- 🕸 Neo4j Knowledge Graph
- 📄 PDF Upload & Incremental Indexing
- 🔁 Duplicate upload prevention
- 📌 Source and page level citations


to provide accurate, source grounded answers from aviation investigation documents.

---

# 🚀 Features

### ✅ Retrieval-Augmented Generation (RAG)

- FAISS Vector Database
- SentenceTransformer Embeddings
- MMR Retrieval
- Source Grounding
- Page level Citations
- Configurable Top K retrieval

---

### ✅ LangGraph Workflow

Agentic routing automatically selects the best retrieval strategy:

```
             User Query
                 │
                 ▼
              LangGraph Router
         ┌────────┼────────┐
         ▼        ▼        ▼
   Metadata   Knowledge   Vector
    Search      Graph     Search
```

---

### ✅ Triple Search Modes

Users can search:

- Aviation Database
- Uploaded Documents
- Both

When Both is selected, retrieval is balanced between the aviation and uploaded document FAISS indexes.

---

### ✅ Upload New PDFs

Upload any aviation report through Streamlit.

The system:

- Computes a SHA-256 file hash
- Detects previously indexed files
- Saves PDF locally
- Splits into chunks
- Generates embeddings
- Updates FAISS incrementally

No rebuilding required.

---

### ✅ Metadata Search

Fast structured lookup using

```
data/metadata/reports.json
```

Supports queries such as

- Report ID
- Airline
- Aircraft
- Keywords
- PDF Name

---

### ✅ Knowledge Graph

Neo4j stores structured aviation relationships.

Example:

```
Report
   │
   ├── OPERATED_BY ──→ Airline
   ├── INVOLVES ─────→ Aircraft
   └── HAS_KEYWORD ──→ Keyword

```

Supports relationship based queries.

---

# 🏗 Project Architecture

```
                           User
                            │
                            ▼
                      Streamlit UI
                            │
                            ▼
                     LangGraph Router
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          Metadata        Neo4j         Vector
           Search          KG            Search
              │             │        ┌────┴────┐
              │             │        ▼         ▼
              │             │     Aviation   Uploaded
              │             │       FAISS      FAISS
              │             │        │         │
              └─────────────┴────────┴─────────┘
                            │
                            ▼
                    Retrieved Context
                            │
                            ▼
                        Groq LLM
                            │
                            ▼
                      Final Answer
```

---

# 📂 Project Structure

```
AeroIntel_AI
│
├── app/
│   ├── langgraph/
│   ├── rag/
│   ├── retrieval/
│   ├── upload/
│   ├── knowledge_graph/
│   ├── config/
│   └── ui/
│
├── data/
│   ├── raw/
│   ├── metadata/
│   │   └── reports.json
│   ├── uploaded/
│   │   └── indexed_files.json
│   └── vector_store/
│       ├── aviation_index/
│       └── uploaded_index/
│
├── build_graph.py
├── build_index.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

Clone repository

```bash
git clone https://github.com/sufiyan438/AeroIntel

cd AeroIntel_AI
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a file named

```
.env
```

Example

```env
GROQ_API_KEY=your_groq_api_key
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

> **Note:** The `.env` file is **not included** in the repository. Use your own Groq API key.

---
# 🐳 Neo4j with Docker Compose

Example docker-compose.yml:
```
services:
  neo4j:
    image: neo4j:5
    container_name: aero-neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: ${NEO4J_USERNAME}/${NEO4J_PASSWORD}
    volumes:
      - neo4j_data:/data

volumes:
  neo4j_data:
```

Start Neo4j:

docker compose up -d

7474 --- Neo4j Browser

7687 --- Bolt connection used by Python

---

# 📚 Building the Aviation Index

Place aviation investigation PDFs in:

data/raw/

Then run:

python build_index.py

PDFs → Load Pages → Chunk → Embed → FAISS aviation_index

This rebuilds the aviation index from the PDFs in data/raw/.

---
# 🗂 Metadata
Structured metadata is maintained in:

data/metadata/reports.json

Example:

{
  "report_id": "AIR2504",
  "title": "In-Flight Separation of Left Mid Exit Door Plug",
  "airline": "Alaska Airlines",
  "aircraft": "Boeing 737-9",
  "registration": "N704AL",
  "keywords": [
    "door plug",
    "rapid depressurization",
    "flight 1282"
  ],
  "pdf": "AIR2504.pdf"
}

Currently, adding a PDF to data/raw/ does not automatically create
its metadata entry. reports.json acts as a curated structured metadata
catalog and may represent only a subset of the raw document corpus.

---

# ▶ Running the Application

```bash
docker compose up -d
streamlit run app/ui/streamlit_app.py --server.fileWatcherType none
```

---

# 📤 Uploading Custom PDFs

Users can upload PDFs directly through the Streamlit interface.

Uploaded reports are:

- Hashed with SHA-256
- Checked against the upload registry
- Stored locally
- Parsed with PyMuPDF
- Chunked
- Embedded
- Indexed incrementally to the uploaded FAISS index
- Registered after successful indexing

No manual indexing is required.

---

# 🗂 Updating Metadata

Metadata is maintained manually.

Update

```
data/metadata/reports.json
```

Example

```json
{
    "report_id":"AIR2504",
    "title":"In-Flight Separation of Left Mid Exit Door Plug",
    "airline":"Alaska Airlines",
    "aircraft":"Boeing 737-9",
    "registration":"N704AL",
    "keywords":[
        "door plug",
        "rapid depressurization"
    ],
    "pdf":"AIR2504.pdf"
}
```

---
# 🕸 Building the Knowledge Graph

After modifying `reports.json`, rebuild the Neo4j graph

Start Neo4j:

docker compose up -d

Build the graph:

```bash
python build_graph.py
```

---

# 🧠 Technologies Used

- Python
- LangChain
- LangGraph
- FAISS
- Neo4j
- Sentence Transformers
- HuggingFace Embeddings
- Groq API
- Streamlit
- PyMuPDF
- Docker / Docker Compose

---

# 📌 Current Limitations

- Metadata is manually maintained.
- Adding PDFs to data/raw/ does not automatically generate structured metadata.
- Knowledge Graph requires manual graph rebuild.
- Uploaded PDFs are indexed in FAISS but are not automatically inserted into Neo4j.
- Knowledge Graph currently supports limited relationship queries.

---

# 🚀 Future Improvements

- Automatic metadata extraction using LLMs
- Automatic synchronization between data/raw/ and reports.json
- Automatic Knowledge Graph updates for new and uploaded reports
- Conversational memory
- GraphRAG integration
- Richer graph entities such as causes, contributing factors, locations and event types
- Multi-document comparison
- Automatic report downloader
- Metadata management interface

---

# 👨‍💻 Author

**Sufiyan**

M.Tech Computer Science & Engineering

Motilal Nehru National Institute of Technology (MNNIT), Prayagraj

---

⭐ If you found this project useful, consider giving it a Star!