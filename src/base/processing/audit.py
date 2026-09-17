import json
from collections import Counter

from config import PROCESSED_CARDS_FILE

def load_processed_cards() -> list[dict]:
    with PROCESSED_CARDS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)

def main() -> None:
    cards = load_processed_cards()

    type_counter = Counter()
    missing_text = 0
    missing_name = 0
    missing_description = 0
    missing_metadata = 0

    for card in cards:
        text = card.get("text", "")
        metadata = card.get("metadata", {})

        card_type = metadata.get("type")
        if card_type:
            type_counter[card_type] += 1

        if not text.strip():
            missing_text += 1

        if not metadata.get("name"):
            missing_name += 1

        if "Descrição/Efeito:" not in text:
            missing_description += 1

        required_metadata = ["id", "name", "type", "frame_type"]

        if any(
            metadata.get(field) is None
            for field in required_metadata
        ):
            missing_metadata += 1

    print("\n=== TIPOS DE CARTA ===")
    for card_type, quantity in type_counter.most_common():
        print(f"{card_type}: {quantity}")

    print("\n=== CAMPOS AUSENTES")
    print(f"Texto vazio: {missing_text}")
    print(f"Nome ausente: {missing_name}")
    print(f"Descrição ausente: {missing_description}")
    print(f"Metadata ausente: {missing_metadata}")

if __name__=="__main__":
    main()