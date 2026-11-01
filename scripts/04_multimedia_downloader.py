import argparse
import json
import os
import shutil
import signal
import sys
import time
from pathlib import Path

import requests

INTERRUPTED = False


def handle_interrupt(signum, frame):
    global INTERRUPTED
    INTERRUPTED = True
    print("\nInterruzione richiesta dall'utente. Chiusura controllata...")
    raise KeyboardInterrupt


signal.signal(signal.SIGINT, handle_interrupt)


def sanitize_filename(name: str) -> str:
    for ch in '\\/:*?"<>|':
        name = name.replace(ch, "_")
    return name.strip()[:180] or "item"


def fetch_anime_page(page: int, per_page: int = 50):
    query = """
    query ($page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        pageInfo {
          total
          currentPage
          lastPage
          hasNextPage
        }
        media(type: ANIME, sort: POPULARITY_DESC) {
          id
          title {
            romaji
            english
            native
          }
          coverImage {
            large
            medium
          }
          genres
        }
      }
    }
    """
    payload = {"query": query, "variables": {"page": page, "perPage": per_page}}
    response = requests.post(
        "https://graphql.anilist.co",
        json=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def fetch_manga_page(page: int, per_page: int = 50):
    query = """
    query ($page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        pageInfo {
          total
          currentPage
          lastPage
          hasNextPage
        }
        media(type: MANGA, sort: POPULARITY_DESC) {
          id
          title {
            romaji
            english
            native
          }
          coverImage {
            large
            medium
          }
          genres
        }
      }
    }
    """
    payload = {"query": query, "variables": {"page": page, "perPage": per_page}}
    response = requests.post(
        "https://graphql.anilist.co",
        json=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def fetch_games_page(page: int, per_page: int = 20):
    # RAWG API demo: can be replaced with IGDB or a custom filtered source
    api_key = os.environ.get("RAWG_API_KEY")
    if not api_key:
        raise RuntimeError("RAWG_API_KEY non settata. Imposta la variabile d'ambiente RAWG_API_KEY oppure usa anime/manga.")
    url = "https://api.rawg.io/api/games"
    params = {
        "key": api_key,
        "page": page,
        "page_size": per_page,
        "genres": "anime,manga,visual-novel,jrpg",
        "ordering": "-released",
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def download_file(url: str, dest_path: Path):
    if dest_path.exists():
        return
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    dest_path.write_bytes(response.content)


def get_type_items(kind: str, page: int):
    if kind == "anime":
        return fetch_anime_page(page)
    if kind == "manga":
        return fetch_manga_page(page)
    if kind == "games":
        return fetch_games_page(page)
    raise ValueError(f"Tipo non supportato: {kind}")


def get_item_title_and_image(item: dict, kind: str):
    if kind in {"anime", "manga"}:
        title_obj = item.get("title", {})
        title = (
            title_obj.get("english")
            or title_obj.get("romaji")
            or title_obj.get("native")
            or f"{kind}_{item.get('id')}"
        )
        image = item.get("coverImage", {})
        image_url = image.get("large") or image.get("medium")
        return title, image_url

    title = item.get("name") or item.get("slug") or f"game_{item.get('id')}"
    image_url = None
    for key in ("background_image", "image_background"):
        image_url = item.get(key)
        if image_url:
            break
    return title, image_url


def process_anime_or_manga(kind: str, output_dir: Path, limit: int | None, resume: bool):
    metadata = []
    downloaded = 0
    page = 1

    while True:
        try:
            data = get_type_items(kind, page)
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print(f"Errore nel fetch {kind}: {exc}")
            break

        media_list = data.get("data", {}).get("Page", {}).get("media", []) if kind in {"anime", "manga"} else data.get("results", [])
        if not media_list:
            print(f"Nessun risultato per {kind} nella pagina {page}.")
            break

        for item in media_list:
            if limit is not None and downloaded >= limit:
                print(f"Limite raggiunto ({limit}). Download interrotto.")
                return metadata

            title, image_url = get_item_title_and_image(item, kind)
            if not image_url:
                continue

            filename = f"{sanitize_filename(title)}_{item.get('id')}.jpg"
            dest = output_dir / filename

            if resume and dest.exists():
                print(f"[{downloaded}] Salto (già presente): {title}")
                continue

            try:
                download_file(image_url, dest)
                metadata.append({
                    "id": item.get("id"),
                    "title": title,
                    "type": kind,
                    "image_url": image_url,
                    "filename": filename,
                })
                downloaded += 1
                print(f"[{downloaded}] Saved in {kind}: {title}")
            except Exception as exc:
                print(f"Errore per {title}: {exc}")

            if limit is not None and downloaded >= limit:
                print(f"Limite raggiunto ({limit}). Download interrotto.")
                return metadata

        page_info = data.get("data", {}).get("Page", {}).get("pageInfo", {}) if kind in {"anime", "manga"} else {}
        if kind in {"anime", "manga"} and not page_info.get("hasNextPage"):
            break
        if kind == "games" and page >= 10:
            break

        page += 1
        time.sleep(0.5)

    return metadata


def main():
    parser = argparse.ArgumentParser(description="Downloader di anime, manga e giochi a tema anime/manga")
    parser.add_argument("--type", choices=["anime", "manga", "games"], default="anime", help="Tipo da scaricare")
    parser.add_argument("--limit", type=int, default=None, help="Numero massimo di immagini da scaricare")
    parser.add_argument("--resume", action="store_true", help="Salta i file già presenti")
    parser.add_argument("--update", action="store_true", help="Aggiorna solo i file nuovi")
    parser.add_argument("--output-dir", default="output", help="Cartella di output")
    args = parser.parse_args()

    output_root = Path(args.output_dir)
    target_dir = output_root / args.type
    target_dir.mkdir(parents=True, exist_ok=True)

    if args.update:
        # se update, rimuove solamente eventuali cartelle vuote/vecchie e continua
        for child in target_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)

    try:
        metadata = process_anime_or_manga(args.type, target_dir, args.limit, args.resume)
    except KeyboardInterrupt:
        metadata = []
        print("\nEsecuzione interrotta dall'utente.")

    metadata_path = output_root / f"metadata_{args.type}.json"
    try:
        existing = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else []
    except Exception:
        existing = []

    existing.extend(metadata)
    metadata_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDownload completato. Totale file salvati: {len(existing)}")
    print(f"Metadata salvata in: {metadata_path}")


if __name__ == "__main__":
    main()
