from sentence_transformers import SentenceTransformer
from chromadb import Documents, EmbeddingFunction, Embeddings

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

class YugiohEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self):
        self.model = load_embedding_model()

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = self.model.encode(
            input,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    @staticmethod
    def name() -> str:
        return "yugioh_embedding_function"

    def get_config(self) -> dict:
        return {}

    @staticmethod
    def build_from_config(config: dict) -> "YugiohEmbeddingFunction":
        return YugiohEmbeddingFunction()

if __name__ == "__main__":
    model = load_embedding_model()

    text = (
        "Dark Magician is a Level 7 DARK Spellcaster"
        "Normal Monster."
    )

    embedding = create_embedding(model, text)

    print(f"Quantidade de dimensões: {len(embedding)}")
    print(f"Primeiros 5 valores: {embedding[:5]}")

