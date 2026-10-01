import json

from config import (
    PROCESSED_CARDS_FILE,
    PROCESSED_DATA_DIR,
)

EMBEDDINGS_FILE = PROCESSED_DATA_DIR / "embeddings.json"
BATCH_SIZE = 64

def load_processed_cards() -> list[dict]:
    with PROCESSED_CARDS_FILE.open(
        "r",
        encoding="utf-8",
    )as file: 
        return json.load(file)

def save_embeddings(
        embeddings: list[list[float]],
) -> None:
    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with EMBEDDINGS_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            embeddings,
            file,
        )

def generate_embeddings() -> None:
    from base.embeddings.model import load_embedding_model

    cards = load_processed_cards()

    texts = [
        card["text"]
        for card in cards
    ]

    print(f"Cartas carregadas: {len(cards)}")
    print(f"Batch size: {BATCH_SIZE}")
    print("Carregando modelo...")

    model = load_embedding_model()

    print("Gerando embeddings...")

    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    embeddings = embeddings.tolist()

    save_embeddings(embeddings)

    print(
        f"Embeddings gerados: {len(embeddings)}"
    )

    print(
        f"Dimensão dos embeddings: "
        f"{len(embeddings[0])}"
    )

    print(
        f"Salvos em: {EMBEDDINGS_FILE}"
    )

if __name__=="__main__":
    generate_embeddings()
