from sentence_transformers import CrossEncoder

MODEL_NAME = (
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

class YugiohReranker:
    def __init__(self):
        self.model = CrossEncoder(
            MODEL_NAME
        )

    def rerank(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        if not candidates:
            return []
        
        pairs = [
            (
                query,
                candidate["document"],
            )
            for candidate in candidates
        ]

        scores = self.model.predict(
            pairs
        )

        ranked = []

        for candidate, score in zip(
            candidates,
            scores,
        ):
            result = candidate.copy()

            result["rerank_score"] = float(
                score
            )

            ranked.append(result)

        ranked.sort(
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        return ranked[:top_k]


if __name__=="__main__":
    from src.retrieval.hybrid import HybridRetriever

    hybrid = HybridRetriever()
    reranker = YugiohReranker()

    queries = [
        "k9 monsters",
        "cards that can be Special Summoned by Graveyard",
        "DARK monsters with high ATK",
        "cards that negate monsters effects",
        "dark magicians",
        "DARK monsters that can tribute other monsters to be invocate",
    ]

    for query in queries:
        candidates = hybrid.search(
            query,
            top_k=20,
            candidate_k=20,
        )

        results = reranker.rerank(
            query,
            candidates,
            top_k=5,
        )

        print("\n" + "=" * 70)
        print(f"CONSULTA: {query}")
        print("=" * 70)

        for index, result in enumerate(
            results,
            start=1,
        ):
            print(
                f"{index}. "
                f"{result['metadata']['name']}"
            )

            print(
                f"Rerank score: "
                f"{result['rerank_score']:.4f}"
            )

            print(
                f"Semantic rank: "
                f"{result['semantic_rank']}"
            )

            print(
                f"Lexical rank: "
                f"{result['lexical_rank']}"
            )

            print()