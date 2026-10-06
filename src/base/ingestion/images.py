import time
from pathlib import Path

import requests

from config import IMAGES_FILES

from base.processing.processor import load_cards

IMAGES_DIR = IMAGES_FILES
URL_FIELD = "image_url_small"   
DELAY = 0.5                     
TIMEOUT = 15
MAX_RETRIES = 3


def collect_targets(cards: list[dict]) -> list[tuple[str, str]]:
    seen = set()
    targets = []
    for card in cards:
        images = card.get("card_images")
        if not images:
            continue
        img = images[0]
        img_id = str(img["id"])
        if img_id in seen or URL_FIELD not in img:
            continue
        seen.add(img_id)
        targets.append((img_id, img[URL_FIELD]))
    return targets


def download(session: requests.Session, url: str, dest: Path) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=TIMEOUT)
        except requests.RequestException as e:
            print(f"  erro de rede ({e}), tentativa {attempt}/{MAX_RETRIES}")
            time.sleep(2 * attempt)
            continue

        if resp.status_code == 200:
            tmp = dest.with_suffix(".tmp")
            tmp.write_bytes(resp.content)
            tmp.rename(dest)  
            return "ok"

        if resp.status_code in (429, 403):
            print(f"  servidor respondeu {resp.status_code}: parando para não ser bloqueado.")
            return "stop"

        print(f"  status {resp.status_code}, tentativa {attempt}/{MAX_RETRIES}")
        time.sleep(2 * attempt)

    return "error"


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    targets = collect_targets(load_cards())
    pending = [(i, u) for i, u in targets if not (IMAGES_DIR / f"{i}.jpg").exists()]
    print(f"{len(targets)} imagens no total, {len(pending)} faltando.")

    session = requests.Session()
    session.headers["User-Agent"] = "ygo-rag-personal-project"

    ok, failed = 0, []
    for n, (img_id, url) in enumerate(pending, start=1):
        result = download(session, url, IMAGES_DIR / f"{img_id}.jpg")

        if result == "ok":
            ok += 1
        elif result == "stop":
            break
        else:
            failed.append(img_id)

        if n % 100 == 0:
            print(f"{n}/{len(pending)} processadas...")
        time.sleep(DELAY)

    print(f"\nBaixadas: {ok} | Falhas: {len(failed)}")
    if failed:
        print("IDs com falha (rode de novo para tentar apenas essas):", failed[:20])


if __name__ == "__main__":
    main()