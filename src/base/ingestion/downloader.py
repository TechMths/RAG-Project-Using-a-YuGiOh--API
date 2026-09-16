import json

from config import CARDS_FILE, RAW_DATA_DIR
from base.ingestion.client import YugiohAPIClient

def download_cards() -> None:
    client = YugiohAPIClient()

    print("Baixando dados das cartas...")

    data = client.get_all_cards()

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with CARDS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

        print(f"Dados salvos em: {CARDS_FILE}")


if __name__=="__main__":
    download_cards()