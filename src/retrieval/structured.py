import json

from src.config import PROCESSED_CARDS_FILE

def load_card():
    with PROCESSED_CARDS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file) 

class StructuredRetriever:
    def __init__(self):
        self.cards = load_card()

    def search(
        self,
        attribute = None,
        archetype = None,
        card_type = None,
        atk_min = None,
        atk_max = None,
        def_min = None,
        def_max = None,
        level = None,
        rank = None,
        top_k = 20,
    ):
        results = []

        for card in self.cards:
            metadata = card["metadata"]

            if attribute is not None:
                if metadata.get("attribute") != attribute:
                    continue

            if archetype is not None:
                if metadata.get("archetype") != archetype:
                    continue

            if card_type is not None:
                if metadata.get("type") != card_type:
                    continue

            atk = metadata.get("atk")
            
            if atk_min is not None:
                if atk is None or atk < atk_min:
                    continue

            if atk_max is not None:
                if atk is None or atk > atk_max:
                    continue

            defense = metadata.get("def")

            if def_min is not None:
                if defense is None or defense < def_min:
                    continue

            if level is not None:
                if metadata.get("level") != level:
                    continue

            if rank is not None:
                if metadata.get("rank") != rank:
                    continue

            results.append(card)

            if len(results) >= top_k:
                break

        return results


if __name__=="__main__":
    retriever = StructuredRetriever()

    results = retriever.search(
        attribute="DARK",
        atk_min=2500,
        top_k=10
    )

    print("\n" + "=" * 70)
    print("DARK monsters with ATK >= 2500")
    print("=" * 70)

    for index, card in enumerate(results, start=1):
        metadata = card["metadata"]

        print(
            f"{index}. {metadata['name']}"
            f"| ATK: {metadata.get('atk')}"
            f"| Attribute: {metadata.get('attribute')}"
            f"| Type: {metadata.get('type')}"
        )