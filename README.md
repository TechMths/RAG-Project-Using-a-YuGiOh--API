
# 🎴 Yu-Gi-Oh! RAG System 🎴

An AI-powered Retrieval-Augmented Generation (RAG) system designed to retrieve and provide information about Yu-Gi-Oh! cards using natural language queries.

<img width="800" height="450" alt="2026-10-0518-07-09-ezgif com-speed" src="https://github.com/user-attachments/assets/e253fe26-f4eb-49e8-88dc-b5e91c846642" />

The project integrates the Yu-Gi-Oh! public API with a local data storage system, semantic search, and a Large Language Model (LLM) to deliver relevant card information through an interactive interface.

## Features

- **Retrieval-Augmented Generation (RAG):** Combines information retrieval with LLM-generated responses.
- **Semantic Search:** Uses text embeddings to identify relevant cards based on natural language queries.
- **Local Data Storage:** Stores API data locally to minimize external requests and improve efficiency.
- **Vector Database:** Uses ChromaDB to store and retrieve vector embeddings.
- **Local LLM Integration:** Connects to Ollama running Llama 3.2 for response generation.
- **Interactive Interface:** Provides a user interface for interacting with the system.

## Technologies

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Interactive user interface |
| Sentence Transformers | Text embedding generation |
| ChromaDB | Vector database |
| NumPy | Numerical operations |
| Requests | HTTP requests and API integration |
| Ollama | Local LLM inference |
| Llama 3.2 | Language model |
| Yu-Gi-Oh! API | External card data source |

## Architecture

The system follows a RAG pipeline that combines data collection, indexing, retrieval, and response generation.

```text
Yu-Gi-Oh! API
      |
      v
Data Collection
      |
      v
Local Data Storage
      |
      v
Text Processing & Embeddings
      |
      v
ChromaDB
      |
      v
User Query
      |
      v
Information Retrieval
      |
      v
Relevant Context
      |
      v
Ollama (Llama 3.2)
      |
      v
Generated Response
```
 
## Pipeline

The retrieval pipeline is based on a hybrid search strategy, combining different retrieval methods to improve the relevance of the results.

### Hybrid Retrieval Pipeline

```text
User Query
    |
    v
  Parser
    |
    +-------------------+
    |                   |
    v                   v
Semantic Retriever   Lexical Retriever
    |                   |
    +--------+----------+
             |
             v
        Structured
        Retrieval
             |
             v
          Reranker
             |
             v
      Relevant Results
             |
             v
      LLM (Llama 3.2)
             |
             v
        Final Response
```

## How It Works

1. **Data Collection:** The system retrieves card information from the Yu-Gi-Oh! API.
2. **Local Storage:** Retrieved data is stored locally to reduce unnecessary API requests.
3. **Embedding Generation:** Card information is transformed into vector embeddings using Sentence Transformers.
4. **Indexing:** Embeddings are stored in ChromaDB to enable efficient similarity-based retrieval.
5. **Query Processing:** User queries are processed to retrieve relevant card information.
6. **Response Generation:** Retrieved information is provided as context to Llama 3.2 through Ollama.
7. **Final Output:** The system generates a response based on the retrieved data.

## Requirements

- Python 3.11+
- Ollama
- Llama 3.2
- Required Python dependencies

## Installation

Clone the repository:

```bash
git clone https://github.com/TechMths/RAG-Project-Using-a-YuGiOh--API.git
cd RAG-Project-Using-a-college-project
```

Install the dependencies:

```bash
pip install -r requirements.txt
uv run python -m src.base.ingestion.downloader
uv run python -m src.base.ingestion.images (this is going to take a time to finish)
uv run python -m src.base.ingestion.processor
uv run python -m src.base.embbedings.generator
uv run python -m src.base.vectorstore.ingest
```

Download the Llama 3.2 model:

```bash
ollama pull llama3.2
```

## Running the Project

Start the backend:

```bash
uv run streamlit run app/app.py
```

## Project Goals

This project was developed to explore and apply concepts related to:

- Retrieval-Augmented Generation (RAG).
- Natural Language Processing (NLP).
- Semantic and hybrid information retrieval.
- Vector databases and embeddings.
- Local LLM deployment.
- API integration and data persistence.
- Backend development with Python.

## Future Improvements

- Improve retrieval accuracy and relevance.
- Optimize query processing and ranking.
- Evaluate retrieval performance using dedicated metrics.
- Improve response generation and context management.
- Expand the user interface and system capabilities.

## License

This project is intended for educational and portfolio purposes. All of the data was requested by the API Yu-Gi-Oh! API by YGOPRODeck. All materials displayed in this project belong to KONAMI. All intellectual property rights are reserved to the respective brand.
