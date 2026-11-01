import json
import os
import random
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

OUTPUT_ROOT = Path("output/dataset")
PER_PAGE = 50
MAX_PAGES = 20
SLEEP_SECONDS = 0.5
MAX_WORKERS = min(32, os.cpu_count() or 4)


def sanitize_filename(name: str) -> str:
    for ch in '\\/:*?"<>|':
        name = name.replace(ch, "_")
    return name.strip()[:160] or "anime"


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
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    dest_path.write_bytes(response.content)


def assign_split(index: int, total: int):
    if index < total * 0.7:
        return "train"
    elif index < total * 0.9:
        return "val"
    return "test"


def build_dataset_item(anime: dict, split_name: str, output_root: Path):
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
        return None

    genres = anime.get("genres") or ["uncategorized"]
    primary_genre = sanitize_filename(genres[0])
    filename = f"{sanitize_filename(title)}_{anime_id}.jpg"
    final_dir = output_root / split_name / primary_genre
    final_dir.mkdir(parents=True, exist_ok=True)
    dest_path = final_dir / filename

    download_file(image_url, dest_path)

    return {
        "id": anime_id,
        "title": title,
        "genre": primary_genre,
        "split": split_name,
        "filename": str(dest_path.relative_to(output_root)),
        "image_url": image_url,
    }


def main():
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    all_anime = []
    for page in range(1, MAX_PAGES + 1):
        data = fetch_anime_page(page)
        media_list = data.get("data", {}).get("Page", {}).get("media", [])
        if not media_list:
            print(f"Nessun risultato trovata nella pagina {page}.")
            break
        all_anime.extend(media_list)

        page_info = data.get("data", {}).get("Page", {}).get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break
        time.sleep(SLEEP_SECONDS)

    random.shuffle(all_anime)
    total = len(all_anime)
    metadata = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for index, anime in enumerate(all_anime):
            split_name = assign_split(index, total)
            futures.append(executor.submit(build_dataset_item, anime, split_name, OUTPUT_ROOT))

        for future in futures:
            result = future.result()
            if result is not None:
                metadata.append(result)

    metadata_path = OUTPUT_ROOT.parent / "metadata_dataset.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Download completato. Totale poster scaricati: {len(metadata)}")
    print(f"Dataset creato in: {OUTPUT_ROOT}")
    print(f"Metadata salvata in: {metadata_path}")


if __name__ == "__main__":
    main()
