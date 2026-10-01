from retrieval.hybrid import HybridRetriever
from retrieval.parser import parse_query_with_fallback as parse_query
from retrieval.reranker import YugiohReranker

class RetrievalPipeline:
    def __init__(self):
        self.hybrid = HybridRetriever()
        self.reranker = YugiohReranker()

    def search(
        self,
        query: str,
        candidate_k: int=20,
        top_k: int= 5,
    ) -> list[dict]:

        parsed_query = parse_query(query)

        text_query = parsed_query.semantic_text
        filters_query = parsed_query.to_kwargs()

        candidates = self.hybrid.search(
            text_query,
            candidate_k=candidate_k,
            top_k=candidate_k,
            **filters_query,
        )

        reranked = self.reranker.rerank(query, candidates, top_k=candidate_k)

        degree_field = "atk" if parsed_query.atk_degree else "def" if parsed_query.def_degree else None
        degree = parsed_query.atk_degree or parsed_query.def_degree
        has_text = bool(parsed_query.semantic_text.strip())

        if degree_field and not has_text:
            sign = -1 if degree in ("high", "very_high") else 1
            reranked = sorted(
                reranked,
                key=lambda r: (sign * (r["metadata"].get(degree_field) or 0), -r["rerank_score"]),
            )
        elif degree_field and has_text:
            sign = -1 if degree in ("high", "very_high") else 1
            reranked = sorted(
                reranked,
                key=lambda r: (-r["rerank_score"], sign * (r["metadata"].get(degree_field) or 0)),
            )
        else:
            reranked = sorted(reranked, key=lambda r: -r["rerank_score"])

        return reranked[:top_k]

if __name__ == "__main__":
    pipeline = RetrievalPipeline()

    for q in [
        "High ATK Dark monsters",
        "something cheap to summon but sill hits like a truck",
        "strong dark magicians",
    ]:
        results = pipeline.search(q, top_k=5)
        print(q)
        for r in results:
            print(" -", r["metadata"]["name"], r["metadata"].get("atk"), r["metadata"].get("level"))
