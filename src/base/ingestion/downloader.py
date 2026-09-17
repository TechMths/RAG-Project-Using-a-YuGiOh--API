import json
import argparse
from pathlib import Path

from config import CARDS_FILE, RAW_DATA_DIR
from base.ingestion.client import YugiohAPIClient

def save_cards_safely(data: dict, destination: Path) -> None:
    temporary_file = destination.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    temporary_file.replace(destination)

def download_cards(force: bool = False) -> None:
    if CARDS_FILE.exists() and not force:
        print("Dados das cartas já existem localmente.")
        print(f"Arquivo: {CARDS_FILE}")
        print("Nenhuma requisição foi feita à API.")
        return

    client = YugiohAPIClient()

    print("Baixando dados das cartas...")

    data = client.get_all_cards()

    if "data" not in data:
        raise ValueError(
            "Resposta da API não contém o campo 'data'."
        )

    if not isinstance(data["data"], list):
        raise ValueError(
            "O campo 'data' da API não é uma lista."
        )

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    save_cards_safely(data, CARDS_FILE)

    print(f"artas baixadas: {len(data['data'])}")
    print(f"Dados salvos em: {CARDS_FILE}")

    #with CARDS_FILE.open("w", encoding="utf-8") as file:
        #json.dump(
           #data,
            #file,
            #ensure_ascii=False,
            #indent=2
        #)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Baixa os dados das cartas do YGOPRODeck."
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Força uma nova consulta à API."
    )

    args = parser.parse_args()

    download_cards(force=args.force)

if __name__=="__main__":
    main()