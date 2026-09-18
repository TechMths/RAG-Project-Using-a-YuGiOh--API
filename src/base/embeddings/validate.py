import json

from config import PROCESSED_CARDS_FILE
from base.embeddings.generator import EMBEDDINGS_FILE

def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def main() -> None:
    cards = load_json(PROCESSED_CARDS_FILE)
    embeddings = load_json(EMBEDDINGS_FILE)

    print(f"Cartas: {len(cards)}")
    print(f"Embeddings: {len(embeddings)}")

    if len(cards) != len(embeddings):
        raise ValueError(
            "Quantidade de cartas e embeddings não corresponde."
        )

    dimension = len(embeddings[0])

    print(f"Dimensão: {dimension}")

    if any(len(embedding) != dimension for embedding in embeddings):
        raise ValueError(
            "Existem embeddings com dimensões diferentes."
        )

    print("Quantidade de documentos: OK")
    print("Dimensão dos Embeddings: OK")

    print("\n=== Exemplo ===")

    print(f"Carta: {cards[0]['metadata']['name']}")
    print(f"Embeddings: {embeddings[0][:5]}")


if __name__ == "__main__":
    main()
