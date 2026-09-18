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

    documents = [
        "A monster that can be Special Summoned from the Graveyard.",
        "A monster that can be Special Summoned from the hand.",
        "A Spell Card that destroys a monster.",
    ]

    question = (
        "Which monster can be Special Summoned"
        "from the Graveyard?"
    )

    documents_embeddings = [
        create_embedding(model, document)
        for document in documents
    ]

    question_embedding = create_embedding(
        model,
        question,
    )

    results = []

    for document, embedding in zip(
        documents,
        documents_embeddings,
    ):
        similarity = cosine_similarity(
            question_embedding,
            embedding,
        )

        results.append(
            (similarity, document)
        )

    results.sort(reverse=True)

    print("=== RESULTADOS ===")

    for similarity, document in results:
        print(f"\nSimilaridade: {similarity:.4f}")
        print(document)