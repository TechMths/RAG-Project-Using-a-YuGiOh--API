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

def build_card_text(card:dict) -> str:
    parts = [card["name"]]

    if card.get("type"):
        parts.append(f"Tipo: {card['type']}")

    if card.get("humanReadableCardType"):
        parts.append(f"Tipo legível: {card['humanReadableCardType']}")

    if card.get("attribute"):
        parts.append(f"Atributo: {card['attribute']}")

    if card.get("level") is not None:
        parts.append(f"Nível: {card['level']}")

    if card.get("linkval") is not None:
        parts.append(f"Link Rating: {card['linkval']}")

    if card.get("linkmarkers"):
        parts.append(f"Link Markers: {', '.join(card['linkmarkers'])}")

    if card.get("scale") is not None:
        parts.append(f"Pendulum Scale: {card['scale']}")

    if card.get("race"):
        parts.append(f"Raça: {card['race']}")

    if card.get("atk") is not None:
        parts.append(f"ATK: {card['atk']}")

    if card.get("def") is not None:
        parts.append(f"DEF: {card['def']}")

    if card.get("archetype"):
        parts.append(f"Arquétipo: {card['archetype']}")

    if card.get("desc"):
        parts.append(f"\nDescrição/Efeito:\n {card['desc']}")

    if card.get("pend_desc"):
        parts.append(f"\nEfeito Pendulum:\n{card['pend_desc']}")

    return "\n".join(parts)

def build_metadata(card: dict) -> dict:
    metadata = {
        "id": card["id"],
        "name": card["name"],
        "type": card.get("type"),
        "card_type": card.get("humanReadableCardType"),
        "frame_type": card.get("frameType"),
        "race": card.get("race"),
        "attribute": card.get("attribute"),
        "archetype": card.get("archetype"),
        "atk": card.get("atk"),
        "def": card.get("def"),
        "level": card.get("level"),
        "rank": card.get("rank"),
        "linkval": card.get("linkval"),
        "scale": card.get("scale"),
    }

    return metadata


def process_card(card: dict) -> dict:
    return {
        "text": build_card_text(card),
        "metadata": build_metadata(card),
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