import numpy as np

from retrieval.lexical import LexicalRetriever
from retrieval.retriever import YugiohRetriever
from retrieval.structured import StructuredRetriever
from retrieval.parser import QueryPlan, parse_query


RRF_K = 60
DEGREE_PCT = {
    "very_high": 90,
    "high": 75,
    "low": 25, 
    "very_low": 10}

MIN_SAMPLE = 8

class HybridRetriever:
    def __init__(self):
        self.semantic = YugiohRetriever()
        self.lexical = LexicalRetriever()
        self.structured = StructuredRetriever()
        self.parse = QueryPlan()

    @staticmethod
    def apply_degree(results, field, degree):
        valued = [r for r in results if r["metadata"].get(field) is not None]
        if not valued:
            return results

        descending = degree in ("high", "very_high")
        values = [r["metadata"][field] for r in valued]

        if len(values) >= MIN_SAMPLE:
            threshold = np.percentile(values, DEGREE_PCT[degree])
            keep = [
                r for r in valued
                if (r["metadata"][field] >= threshold if descending
                    else r["metadata"][field] <= threshold)
            ]
        else:
            keep = valued

        return sorted(keep, key=lambda r: r["metadata"][field], reverse=descending)

    def search(
        self,
        query: str,
        top_k: int = 5,
        candidate_k: int = 20,
        attribute = None,
        archetype = None,
        card_type = None,
        atk_degree = None,
        atk_min = None,
        atk_max = None,
        def_degree = None,
        def_min = None,
        def_max = None,
        level = None,
        level_min = None,
        level_max = None,
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

        has_structured_filters = any(
            value is not None
            for value in [
                attribute,
                archetype,
                card_type,
                atk_degree,
                atk_min,
                atk_max,
                def_degree,
                def_min,
                def_max,
                level,
                level_min,
                level_max,
                rank,
            ]
        )

        structured_results = (self.structured.search(
            attribute=attribute,
            archetype=archetype,
            card_type=card_type,
            atk_degree=atk_degree,
            atk_min=atk_min,
            atk_max=atk_max,
            def_degree=def_degree,
            def_min=def_min,
            def_max=def_max,
            level=level,
            level_min=level_min,
            level_max=level_max,
            rank=rank,
            top_k=None,
        ) if has_structured_filters else [])

        if atk_degree:
            structured_results = self.apply_degree(structured_results, "atk", atk_degree)

        if def_degree:
            structured_results = self.apply_degree(structured_results, "def", def_degree)

        use_text = bool(query.strip())
        semantic_results = self.semantic.search(query, top_k=candidate_k) if use_text else []
        lexical_results = self.lexical.search(query, top_k=candidate_k) if use_text else []


        structured_ids = {
            result["metadata"]["id"]
            for result in structured_results
        }

        candidates = {}
            
        for rank, result in enumerate(
            semantic_results,
            start=1,
        ): 
            card_id = result["metadata"]["id"]

            if has_structured_filters and card_id not in structured_ids:
                continue

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

            if has_structured_filters and card_id not in structured_ids:
                continue

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

            if card_id in candidates:
                candidates[card_id]["structured_rank"] = True

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

        degree_field = "atk" if atk_degree else "def" if def_degree else None
        degree = atk_degree or def_degree
        has_text = bool(query.strip())

        if degree_field and not has_text:
            sign = -1 if degree in ("high", "very_high") else 1
            ranked = sorted(
                candidates.values(),
                key=lambda c: (sign * (c["metadata"].get(degree_field) or 0), -c["score"]),
            )
        elif degree_field and has_text:
            sign = -1 if degree in ("high", "very_high") else 1
            ranked = sorted(
                candidates.values(),
                key=lambda c: (-c["score"], sign * (c["metadata"].get(degree_field) or 0)),
            )
        else:
            ranked = sorted(candidates.values(), key=lambda c: c["score"], reverse=True)

        return ranked[:top_k]

if __name__=="__main__":
    retriever = HybridRetriever()

    inputs = ["Dark Magician",
              "cards similar to Dark Magician",
              "Alsei, the Sylvan High Protector",
              "High ATK Dark Monsters",
              ]

    for i in inputs:
        print("="*20)
        print(i)
        print("="*20)

        query = parse_query(i)

        results = retriever.search(query.semantic_text, top_k=10, **query.to_kwargs())

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
                f"| DEF: "
                f"{metadata.get('def')}"
                f"| Level: "
                f"{metadata.get('level')}"
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

