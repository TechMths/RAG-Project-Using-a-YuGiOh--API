from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def load_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)

def create_embedding(
    model: SentenceTransformer,
    text: str,
) -> list[float]:
    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()

if __name__ == "__main__":
    model = load_embedding_model()

    text = (
        "Dark Magician is a Level 7 DARK Spellcaster"
        "Normal Monster."
    )

    embedding = create_embedding(model, text)
    print(f"Quantidade de dimensões: {len(embedding)}")
    print(f"Primeiros 5 valores: {embedding[:5]}")

