import json

from config import CARDS_FILE

def load_cards() -> list[dict]:
    with CARDS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)["data"]


def main()->None:
    cards = load_cards()

    monster = next(
        card for card in cards
        if "Monster" in card["type"]
    )

    spell = next(
        card for card in cards
        if card["type"] == "Spell Card"
    )

    trap = next(
        card for card in cards
        if card["type"] == "Trap Card"
    )

    print("=== MONSTRO ===")
    print(sorted(monster.keys()))

    print("\n=== SPELL ===")
    print(sorted(spell.keys()))

    print("\n=== TRAP ===")
    print(sorted(trap.keys()))

if __name__=="__main__":
    main()

