from base.embeddings.model import (
    create_embedding,
    load_embedding_model,
)

def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Os vetores precisam ter a mesma dimensão;"
        )

    return sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

if __name__=="__main__":
    model = load_embedding_model()

    texts = [
        "A monster that can be Special Summoned from the Graveyard.",
        "A monster that can be Special Summoned from the hand.",
        "A Spell Card that destroys a monster.",
    ]

    embeddings = [
        create_embedding(model, text)
        for text in texts
    ]

    print("=== SIMILARIDADES ===")

    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            similarity = cosine_similarity(
                embeddings[i],
                embeddings[j],
            )

            print(
                f"Texto {i + 1} * Texto {j + 1}: "
                f"{similarity:.4f}"
            )

