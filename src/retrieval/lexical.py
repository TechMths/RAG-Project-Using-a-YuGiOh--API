import json
import re
import math
from collections import Counter

from config import PROCESSED_CARDS_FILE

def load_cards() -> list[dict]:
    with PROCESSED_CARDS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)

def tokenize(text: str) -> set[str]:
    return set(
        re.findall(
            r"\b\w+\b",
            text.lower(),
        )
    )

class LexicalRetriever:
    def __init__(self):
        self.cards = load_cards()

        self.document_frequency = Counter()

        for card in self.cards:
            tokens = set(
                tokenize(card["text"])
            )

            for token in tokens:
                self.document_frequency[token] += 1

        self.total_documents = len(
            self.cards
        )

    def idf(self, token: str) -> float:
        document_frequency = (
            self.document_frequency.get(
                token,
                0
            )
        )

        return math.log(
            (
                self.total_documents + 1
            )
            /
            (
                document_frequency + 1
            )
        ) + 1

    def search(
        self,
        query:str,
        top_k:int=5,
    ) -> list[dict]:
        
        query_tokens = tokenize(query)

        scored_cards = []

        for card in self.cards:
            card_tokens = tokenize(
                card["text"]
            )

            token_counts = Counter(
                card_tokens
            ) 

            score = 0.0

            for token in query_tokens:
                if token in token_counts:
                    score += self.idf(token)

            if score > 0:
                scored_cards.append(
                    (
                        score,
                        card,
                    )
                )

        scored_cards.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        results = []

        for score, card in scored_cards[:top_k]:
            results.append(
                {
                    "document": card["text"],
                    "metadata": card["metadata"],
                    "score": score,
                }
            )

        return results

if __name__=="__main__":
    retriever = LexicalRetriever()

    queries = [
        "k9 monsters",
        "cards that can be Special Summoned by Graveyard",
        "DARK monsters with high ATK",
        "cards that negate monsters effects",
        "dark magicians",
    ]

    for query in queries:
        print("\n" + "=" * 70)
        print(f"CONSULTA: {query}")
        print("=" * 70)

        results = retriever.search(
            query,
            top_k=5,
        )

        for index, result in enumerate(
            results,
            start=1,
        ):
            print(
                f"{index}. "
                f"{result['metadata']['name']}"
                f"| score: {result['score']:.4f}"
            )