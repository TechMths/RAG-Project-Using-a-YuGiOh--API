import json

from config import (
    CARDS_FILE, 
    PROCESSED_CARDS_FILE, 
    PROCESSED_DATA_DIR,
)

def load_cards() -> list[dict]:
    with CARDS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data["data"]


def process_card(card: dict) -> dict:
    return {
        "text": f"{card['name']}\n\n{card['desc']}",
        "metadata": {
            "id": card["id"],
            "name": card["name"],
            "type": card["type"],
            "card_type": card.get("humanReadableCardType"),
            "frame_type": card["frameType"],
            "race": card.get("race"),
            "archetype": card.get("archetype"),
        },
    }

def process_cards() -> list[dict]:
    cards = load_cards()

    process_cards = [
        process_card(card)
        for card in cards
    ]

    return process_cards

def save_processed_cards(cards: list[dict]) -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with PROCESSED_CARDS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            cards,
            file,
            ensure_ascii=False,
            indent=2,
        )

if __name__=="__main__":
    cards = process_cards()

    save_processed_cards(cards)

    print(f"Cartas processadas: {len(cards)}")
    print(f"Dados salvos em: {PROCESSED_CARDS_FILE}")