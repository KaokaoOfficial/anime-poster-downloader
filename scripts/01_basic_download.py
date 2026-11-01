import os
import json
import time
import requests
from pathlib import Path

OUTPUT_DIR = Path("output/basic")
PER_PAGE = 50
MAX_PAGES = 20
SLEEP_SECONDS = 1.0


def sanitize_filename(name: str) -> str:
    invalid_chars = "\\/:*?\"<>|"
    for ch in invalid_chars:
        name = name.replace(ch, "_")
    return name.strip()[:180] or "anime"


def fetch_anime_page(page: int):
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
    payload = {"query": query, "variables": {"page": page, "perPage": PER_PAGE}}
    response = requests.post(
        "https://graphql.anilist.co",
        json=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def download_file(url: str, dest_path: Path):
    if dest_path.exists():
        return
    destination = dest_path.parent
    destination.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    dest_path.write_bytes(response.content)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = []
    downloaded = 0

    for page in range(1, MAX_PAGES + 1):
        data = fetch_anime_page(page)
        media_list = data.get("data", {}).get("Page", {}).get("media", [])

        if not media_list:
            print(f"Nessun risultato trovato nella pagina {page}.")
            break

        for anime in media_list:
            anime_id = anime.get("id")
            title_obj = anime.get("title", {})
            title = (
                title_obj.get("english")
                or title_obj.get("romaji")
                or title_obj.get("native")
                or f"anime_{anime_id}"
            )
            image_url = anime.get("coverImage", {}).get("large") or anime.get("coverImage", {}).get("medium")
            if not image_url:
                continue

            filename = f"{sanitize_filename(title)}_{anime_id}.jpg"
            dest = OUTPUT_DIR / filename
            try:
                download_file(image_url, dest)
                metadata.append({
                    "id": anime_id,
                    "title": title,
                    "image_url": image_url,
                    "filename": filename,
                    "genres": anime.get("genres", []),
                })
                downloaded += 1
                print(f"[{downloaded}] Downloaded: {title}")
            except Exception as exc:
                print(f"Errore per {title}: {exc}")

        page_info = data.get("data", {}).get("Page", {}).get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break
        time.sleep(SLEEP_SECONDS)

    metadata_path = OUTPUT_DIR.parent / "metadata_basic.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Download completato. Totale file salvati: {downloaded}")
    print(f"Metadata salvata in: {metadata_path}")


if __name__ == "__main__":
    main()
