import json

import chromadb

from config import (
    DATA_DIR,
    PROCESSED_CARDS_FILE,
)

from base.embeddings.generator import EMBEDDINGS_FILE

from base.embeddings.model import YugiohEmbeddingFunction


VECTORSTORE_DIR = DATA_DIR / "vectorstore"

COLLECTION_NAME = "yugioh_cards"

def create_client():
    VECTORSTORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    return chromadb.PersistentClient(
        path=str(VECTORSTORE_DIR)
    )

def load_json(path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)

def get_collection(client):
    embedding_function = YugiohEmbeddingFunction()

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )

def clean_metadata(meta: dict) -> dict:
    return {k: v for k, v in meta.items() if v is not None}

def add_first_card(collection):
    cards = load_json(PROCESSED_CARDS_FILE)
    embeddings = load_json(EMBEDDINGS_FILE)

    card = cards[0]
    embedding = embeddings[0]

    collection.add(
        ids=[str(card["metadata"]["id"])],
        documents=[card["text"]],
        embeddings=[embedding],
        metadatas=[clean_metadata(card["metadata"])],
    )

if __name__=="__main__":
    client = create_client()
    collection = get_collection(client)

    if collection.count() == 0:
        add_first_card(collection)
        
    print(
        f"Quantidade de documentos: "
        f"{collection.count()}"
    )
