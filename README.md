# RAG-Project-Using-a-YuGiOh!-API

Data ingestion

The project retrieves card data from YGOPRODeck API and stores
the raw dataset locally before processing.

The dataset is intentionally excluded from version control.
Run:

uv run python -m yugioh_rag.ingestion.downloader
