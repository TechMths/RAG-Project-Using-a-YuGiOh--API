from src.retrieval.lexical import LexicalRetriever
from src.retrieval.retriever import YugiohRetriever
from src.retrieval.structured import StructuredRetriever


RRF_K = 60


class HybridRetriever:
    def __init__(self):
        self.semantic = YugiohRetriever()
        self.lexical = LexicalRetriever()
        self.structured = StructuredRetriever()

    def search(
        self,
        query: str,
        top_k: int = 5,
        candidate_k: int = 20,
        attribute = None,
        archetype = None,
        card_type = None,
        atk_min = None,
        atk_max = None,
        def_min = None,
        def_max = None,
        level = None,
        rank = None,
    ) -> list[dict]:
        
        semantic_results = self.semantic.search(
            query,
            top_k=candidate_k,
        )

        lexical_results = self.lexical.search(
            query,
            top_k=candidate_k
        )

        structured_results = self.structured.search(
            attribute=attribute,
            archetype=archetype,
            card_type=card_type,
            atk_min=atk_min,
            atk_max=atk_max,
            def_min=def_min,
            def_max=def_max,
            level=level,
            rank=rank,
            top_k=candidate_k,
        )

        candidates = {}
            
        for rank, result in enumerate(
            semantic_results,
            start=1,
        ): 
            card_id = result["metadata"]["id"]

            candidates.setdefault(
                card_id,
                {
                    **result,
                    "semantic_rank": None,
                    "lexical_rank": None,
                    "structured_rank": None,
                    "score": 0.0,
                },
            )

            candidates[card_id]["semantic_rank"] = rank
            candidates[card_id]["score"] += 1 / (RRF_K + rank)

        for rank, result in enumerate(
            lexical_results,
            start=1,
        ):
            card_id = result["metadata"]["id"]

            candidates.setdefault(
                card_id,
                {
                    **result,
                    "semantic_rank": None,
                    "lexical_rank": None,
                    "structured_rank": None,
                    "score": 0.0,
                },
            )

            candidates[card_id]["lexical_rank"] = rank
            candidates[card_id]["score"] += 1 / (RRF_K + rank)

        for rank, result in enumerate(structured_results, start=1):
            metadata = result["metadata"]
            card_id = metadata["id"]

            candidates.setdefault(
                card_id,
                {
                    "document": result["text"],
                    "metadata": metadata,
                    "semantic_rank": None,
                    "lexical_rank": None,
                    "structured_rank": None,
                    "score": 0.0,
                },
            )

            candidates[card_id]["structured_rank"] = rank
            candidates[card_id]["score"] += 1 / (RRF_K + rank)

        ranked = sorted(
            candidates.values(),
            key=lambda item: item["score"],
            reverse=True,
        )

        return ranked[:top_k]

if __name__=="__main__":
    retriever = HybridRetriever()

    query = "DARK monsters with high ATK"

    print("\n" + "=" * 70)
    print(f"CONSULTA: {query}")
    print("=" * 70)

    results = retriever.search(
        query,
        top_k=10,
        candidate_k=20,
        attribute="DARK",
        atk_min=2500,
    )

    for index, result in enumerate(
        results,
        start=1,
    ): 
        metadata = result["metadata"]
        
        print(
            f"{index}. "
            f"{metadata['name']}"
            f"| ATK: "
            f"{metadata.get('atk')}"
            f"| Attribute: "
            f"{metadata.get('attribute')}"
            f"| semantic: "
            f"{result['semantic_rank']}"
            f"| lexical: "
            f"{result['lexical_rank']}"
            f"| Structured rank: "
            f"{result['structured_rank']}"
            f"| RRF score: "
            f"{result['score']:.4f}"
        )

