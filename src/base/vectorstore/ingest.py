import json

from config import PROCESSED_CARDS_FILE
from base.embeddings.generator import EMBEDDINGS_FILE
from llm_rag.src.base.vectorstore.store import (
    create_client,
    get_collection,
    clean_metadata,
)


BATCH_SIZE = 500

def load_json(path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)

def load_data():
    cards = load_json(PROCESSED_CARDS_FILE)
    embeddings = load_json(EMBEDDINGS_FILE)

    if len(cards) != len(embeddings):
        raise ValueError(
            "Quantidade de cartas e embeddings não corresponde."
        )

    return cards, embeddings

def ingest_cards(collection) -> None:
    cards, embeddings = load_data()

    total = len(cards)

    print(f"Cartas carregas: {total}")
    print(f"Batch size: {BATCH_SIZE}")
    print("Iniciando ingestão no ChromaDB...")

    for start in range(0, total, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total)

        batch_cards = cards[start:end]
        batch_embeddings = embeddings[start:end]

        ids = [
            str(card["metadata"]["id"])
            for card in batch_cards
        ]

        documents = [
            card["text"]
            for card in batch_cards
        ]

        metadatas = [
            clean_metadata(card["metadata"])
            for card in batch_cards
        ]

        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=batch_embeddings,
            metadatas=metadatas,
        )

        print(
            f"Processadas: {end}/{total}"
        )

def main() -> None:
    client = create_client()
    collection = get_collection(client)

    ingest_cards(collection)

    print()
    print(
        f"Documentos no ChromaDB:"
        f"{collection.count()}"
    )

if __name__=="__main__":
    main()