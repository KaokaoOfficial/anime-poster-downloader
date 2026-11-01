import argparse
import json
import locale
import os
import re
import signal
import sys
import time
from pathlib import Path

import requests

SUPPORTED_LANGS = {
    "en": "English",
    "it": "Italiano",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "ja": "日本語",
    "ru": "Русский",
}

TEXT = {
    "en": {
        "title": "Advanced Anime/Manga/Game Download Manager",
        "choose_mode": "Choose output mode:",
        "mode_single": "1) Single folder",
        "mode_genre": "2) By genre",
        "choose_type": "Choose content type:",
        "type_all": "1) All (anime + manga + games)",
        "type_anime": "2) Anime only",
        "type_manga": "3) Manga only",
        "type_games": "4) Games only",
        "limit_prompt": "How many items per type do you want to download? (write 'all' or a number):",
        "lang_prompt": "Choose language for the prompts:",
        "auto_detected": "System language detected automatically: {lang}",
        "no_games_key": "RAWG_API_KEY not found. Games will be skipped.",
        "downloaded": "Downloaded: {title}",
        "skipped": "Skipped because it already exists: {title}",
        "limit_hit": "Limit reached for {type}. Stopping current download.",
        "done": "Done. Total saved: {count}",
        "metadata": "Metadata saved in: {path}",
        "invalid_input": "Invalid input. Using default.",
        "processing": "Processing: {type}",
        "custom_path": "Output directory:",
        "exit_prompt": "Press Enter to exit...",
    },
    "it": {
        "title": "Gestore avanzato download anime/manga/giochi",
        "choose_mode": "Scegli la modalità di salvataggio:",
        "mode_single": "1) Cartella unica",
        "mode_genre": "2) Per genere",
        "choose_type": "Scegli il tipo di contenuto:",
        "type_all": "1) Tutti (anime + manga + giochi)",
        "type_anime": "2) Solo anime",
        "type_manga": "3) Solo manga",
        "type_games": "4) Solo giochi",
        "limit_prompt": "Quanti elementi per tipo vuoi scaricare? (scrivi 'all' o un numero):",
        "lang_prompt": "Scegli la lingua per i prompt:",
        "auto_detected": "Lingua del sistema rilevata automaticamente: {lang}",
        "no_games_key": "RAWG_API_KEY non trovato. I giochi verranno saltati.",
        "downloaded": "Scaricato: {title}",
        "skipped": "Saltato perché esiste già: {title}",
        "limit_hit": "Limite raggiunto per {type}. Interruzione del download.",
        "done": "Completato. Totale salvati: {count}",
        "metadata": "Metadati salvati in: {path}",
        "invalid_input": "Input non valido. Uso il valore predefinito.",
        "processing": "Elaborazione: {type}",
        "custom_path": "Cartella di output:",
        "exit_prompt": "Premi Invio per uscire...",
    },
    "es": {
        "title": "Gestor avanzado de descarga de anime/manga/juegos",
        "choose_mode": "Elige el modo de salida:",
        "mode_single": "1) Carpeta única",
        "mode_genre": "2) Por género",
        "choose_type": "Elige el tipo de contenido:",
        "type_all": "1) Todo (anime + manga + juegos)",
        "type_anime": "2) Solo anime",
        "type_manga": "3) Solo manga",
        "type_games": "4) Solo juegos",
        "limit_prompt": "¿Cuántos elementos por tipo quieres descargar? (escribe 'all' o un número):",
        "lang_prompt": "Elige el idioma para los mensajes:",
        "auto_detected": "Idioma del sistema detectado automáticamente: {lang}",
        "no_games_key": "RAWG_API_KEY no encontrado. Los juegos se omitiran.",
        "downloaded": "Descargado: {title}",
        "skipped": "Omitido porque ya existe: {title}",
        "limit_hit": "Límite alcanzado para {type}. Se detiene la descarga.",
        "done": "Hecho. Total guardado: {count}",
        "metadata": "Metadatos guardados en: {path}",
        "invalid_input": "Entrada no válida. Se usa el valor predeterminado.",
        "processing": "Procesando: {type}",
        "custom_path": "Carpeta de salida:",
        "exit_prompt": "Pulsa Enter para salir...",
    },
    "fr": {
        "title": "Gestionnaire avancé de téléchargement anime/manga/jeux",
        "choose_mode": "Choisissez le mode de sortie :",
        "mode_single": "1) Dossier unique",
        "mode_genre": "2) Par genre",
        "choose_type": "Choisissez le type de contenu :",
        "type_all": "1) Tout (anime + manga + jeux)",
        "type_anime": "2) Anime uniquement",
        "type_manga": "3) Manga uniquement",
        "type_games": "4) Jeux uniquement",
        "limit_prompt": "Combien d'éléments par type souhaitez-vous télécharger ? (écrivez 'all' ou un nombre) :",
        "lang_prompt": "Choisissez la langue des invites :",
        "auto_detected": "Langue du système détectée automatiquement : {lang}",
        "no_games_key": "RAWG_API_KEY introuvable. Les jeux seront ignorés.",
        "downloaded": "Téléchargé : {title}",
        "skipped": "Ignoré car il existe déjà : {title}",
        "limit_hit": "Limite atteinte pour {type}. Arrêt du téléchargement.",
        "done": "Terminé. Total enregistré : {count}",
        "metadata": "Métadonnées enregistrées dans : {path}",
        "invalid_input": "Entrée invalide. Valeur par défaut utilisée.",
        "processing": "Traitement : {type}",
        "custom_path": "Dossier de sortie :",
        "exit_prompt": "Appuyez sur Entrée pour quitter...",
    },
    "de": {
        "title": "Erweiterter Downloader für Anime/Manga/Spiele",
        "choose_mode": "Ausgabemodus wählen:",
        "mode_single": "1) Einzelner Ordner",
        "mode_genre": "2) Nach Genre",
        "choose_type": "Inhaltstyp wählen:",
        "type_all": "1) Alles (Anime + Manga + Spiele)",
        "type_anime": "2) Nur Anime",
        "type_manga": "3) Nur Manga",
        "type_games": "4) Nur Spiele",
        "limit_prompt": "Wie viele Elemente pro Typ möchten Sie herunterladen? ('all' oder Zahl eingeben):",
        "lang_prompt": "Sprache für die Meldungen wählen:",
        "auto_detected": "Systemsprache automatisch erkannt: {lang}",
        "no_games_key": "RAWG_API_KEY nicht gefunden. Spiele werden übersprungen.",
        "downloaded": "Heruntergeladen: {title}",
        "skipped": "Übersprungen, da bereits vorhanden: {title}",
        "limit_hit": "Grenze erreicht für {type}. Download wird gestoppt.",
        "done": "Fertig. Gesamt gespeichert: {count}",
        "metadata": "Metadaten gespeichert unter: {path}",
        "invalid_input": "Ungültige Eingabe. Standardwert wird verwendet.",
        "processing": "Verarbeitung: {type}",
        "custom_path": "Ausgabeverzeichnis:",
        "exit_prompt": "Enter drücken, um zu beenden...",
    },
    "ja": {
        "title": "高度なアニメ/漫画/ゲーム ダウンローダー",
        "choose_mode": "出力モードを選択:",
        "mode_single": "1) 1つのフォルダに保存",
        "mode_genre": "2) ジャンル別に保存",
        "choose_type": "コンテンツの種類を選択:",
        "type_all": "1) すべて（アニメ + 漫画 + ゲーム）",
        "type_anime": "2) アニメのみ",
        "type_manga": "3) 漫画のみ",
        "type_games": "4) ゲームのみ",
        "limit_prompt": "1種類あたり何件ダウンロードしますか？ ('all' または数字を入力):",
        "lang_prompt": "表示言語を選択:",
        "auto_detected": "システム言語を自動検出: {lang}",
        "no_games_key": "RAWG_API_KEY が見つかりません。ゲームはスキップされます。",
        "downloaded": "ダウンロード済み: {title}",
        "skipped": "すでに存在するためスキップ: {title}",
        "limit_hit": "{type} の上限に達しました。ダウ��ロードを停止します。",
        "done": "完了。保存件数: {count}",
        "metadata": "メタデータ保存先: {path}",
        "invalid_input": "入力が無効です。デフォルトを使用します。",
        "processing": "処理中: {type}",
        "custom_path": "出力ディレクトリ:",
        "exit_prompt": "Enter を押して終了...",
    },
    "ru": {
        "title": "Расширенный загрузчик аниме/манги/игр",
        "choose_mode": "Выберите режим сохранения:",
        "mode_single": "1) Один каталог",
        "mode_genre": "2) По жанрам",
        "choose_type": "Выберите тип контента:",
        "type_all": "1) Всё (аниме + манга + игры)",
        "type_anime": "2) Только аниме",
        "type_manga": "3) Только манга",
        "type_games": "4) Только игры",
        "limit_prompt": "Сколько элементов на тип хотите скачать? (введите 'all' или число):",
        "lang_prompt": "Выберите язык интерфейса:",
        "auto_detected": "Язык системы определён автоматически: {lang}",
        "no_games_key": "RAWG_API_KEY не найден. Игры будут пропущены.",
        "downloaded": "Скачано: {title}",
        "skipped": "Пропущено, так как уже существует: {title}",
        "limit_hit": "Достигнут лимит для {type}. Загрузка остановлена.",
        "done": "Готово. Всего сохранено: {count}",
        "metadata": "Метаданные сохранены в: {path}",
        "invalid_input": "Некорректный ввод. Используется значение по умолчанию.",
        "processing": "Обработка: {type}",
        "custom_path": "Каталог вывода:",
        "exit_prompt": "Нажмите Enter для выхода...",
    },
}

INTERRUPTED = False


def handle_interrupt(signum, frame):
    global INTERRUPTED
    INTERRUPTED = True
    print("\nInterrupted by user.")
    raise KeyboardInterrupt


signal.signal(signal.SIGINT, handle_interrupt)


def detect_system_language():
    try:
        env_lang = os.environ.get("LANG") or os.environ.get("LC_ALL") or os.environ.get("LC_CTYPE")
        if env_lang:
            code = env_lang.split(".")[0].split("_")[0].lower()
            if code in SUPPORTED_LANGS:
                return code
        locale_name = locale.getdefaultlocale()[0]
        if locale_name:
            code = locale_name.split("_")[0].lower()
            if code in SUPPORTED_LANGS:
                return code
    except Exception:
        pass
    return "en"


def sanitize_filename(value: str) -> str:
    for ch in '\\/:*?"<>|':
        value = value.replace(ch, "_")
    return re.sub(r"\s+", "_", value).strip()[:180] or "item"


def get_type_name(kind: str):
    return {"anime": "anime", "manga": "manga", "games": "games"}.get(kind, kind)


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
          title { romaji english native }
          coverImage { large medium }
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
          title { romaji english native }
          coverImage { large medium }
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
    api_key = os.environ.get("RAWG_API_KEY")
    if not api_key:
        raise RuntimeError("RAWG_API_KEY missing")
    params = {
        "key": api_key,
        "page": page,
        "page_size": per_page,
        "ordering": "-released",
        "genres": "anime,manga,visual-novel,jrpg",
    }
    response = requests.get("https://api.rawg.io/api/games", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def download_file(url: str, dest_path: Path):
    if dest_path.exists():
        return
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    dest_path.write_bytes(response.content)


def get_preferred_title(item, kind: str, lang: str):
    if kind in {"anime", "manga"}:
        title_obj = item.get("title", {})
        preferred = [
            title_obj.get("english"),
            title_obj.get("romaji"),
            title_obj.get("native"),
            f"{kind}_{item.get('id')}",
        ]
        return next((x for x in preferred if x), f"{kind}_{item.get('id')}")
    return item.get("name") or item.get("slug") or f"game_{item.get('id')}"


def get_cover_url(item, kind: str):
    if kind in {"anime", "manga"}:
        cover = item.get("coverImage", {})
        return cover.get("large") or cover.get("medium")
    if kind == "games":
        return item.get("background_image")
    return None


def choose_output_base(output_dir: Path, mode: str, kind: str):
    if mode == "single":
        return output_dir / "all"
    return output_dir / kind


def process_one_kind(kind: str, output_dir: Path, mode: str, limit: int | None, resume: bool, lang: str):
    if kind == "games":
        try:
            page_data = fetch_games_page(1, 10)
        except Exception as exc:
            print(f"Games skipped: {exc}")
            return []
    else:
        page_data = fetch_anime_page(1) if kind == "anime" else fetch_manga_page(1)

    base_dir = choose_output_base(output_dir, mode, kind)
    metadata = []
    saved = 0
    page = 1

    while True:
        try:
            if kind == "anime":
                data = fetch_anime_page(page, 50)
                items = data.get("data", {}).get("Page", {}).get("media", [])
                next_page = data.get("data", {}).get("Page", {}).get("pageInfo", {}).get("hasNextPage", False)
            elif kind == "manga":
                data = fetch_manga_page(page, 50)
                items = data.get("data", {}).get("Page", {}).get("media", [])
                next_page = data.get("data", {}).get("Page", {}).get("pageInfo", {}).get("hasNextPage", False)
            else:
                data = fetch_games_page(page, 20)
                items = data.get("results", [])
                next_page = bool(data.get("next")) and page < 20
            if not items:
                break
            for item in items:
                if limit is not None and saved >= limit:
                    print(f"Limit reached for {kind}: {limit}")
                    return metadata
                title = get_preferred_title(item, kind, lang)
                cover_url = get_cover_url(item, kind)
                if not cover_url:
                    continue
                if mode == "genre":
                    genre_name = "uncategorized"
                    if kind in {"anime", "manga"}:
                        genres = item.get("genres") or ["uncategorized"]
                        genre_name = sanitize_filename(genres[0].lower())
                    target_dir = base_dir / genre_name
                else:
                    target_dir = base_dir
                filename = f"{sanitize_filename(title)}_{item.get('id')}.jpg"
                dest = target_dir / filename
                if resume and dest.exists():
                    continue
                try:
                    download_file(cover_url, dest)
                    metadata.append({
                        "id": item.get("id"),
                        "title": title,
                        "type": kind,
                        "cover_url": cover_url,
                        "filename": str(dest.relative_to(output_dir)),
                        "genre": genre_name if mode == "genre" else "all",
                    })
                    saved += 1
                    print(f"[{saved}] {title} saved in {kind}")
                except Exception as exc:
                    print(f"Error saving {title}: {exc}")
                    continue
            if limit is not None and saved >= limit:
                break
            if not next_page:
                break
            page += 1
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nProcess interrupted by user.")
            break
        except Exception as exc:
            print(f"Error on {kind} page {page}: {exc}")
            break
    return metadata


def interactive_config(default_lang: str):
    print(f"\n{TEXT[default_lang]['title']}\n")
    print(TEXT[default_lang]['choose_mode'])
    print(TEXT[default_lang]['mode_single'])
    print(TEXT[default_lang]['mode_genre'])
    mode_choice = input("[1/2]: ").strip()
    mode = "single" if mode_choice in {"1", "single"} else "genre"

    print("\n" + TEXT[default_lang]['choose_type'])
    print(TEXT[default_lang]['type_all'])
    print(TEXT[default_lang]['type_anime'])
    print(TEXT[default_lang]['type_manga'])
    print(TEXT[default_lang]['type_games'])
    type_choice = input("[1/2/3/4]: ").strip()
    kind_map = {"1": "all", "2": "anime", "3": "manga", "4": "games"}
    selected_type = kind_map.get(type_choice, "all")

    limit_raw = input(f"\n{TEXT[default_lang]['limit_prompt']} ").strip().lower()
    limit = None if limit_raw in {"all", ""} else int(limit_raw)

    print("\n" + TEXT[default_lang]['lang_prompt'])
    for idx, code in enumerate(SUPPORTED_LANGS.keys(), start=1):
        print(f"{idx}) {SUPPORTED_LANGS[code]}")
    lang_choice = input(f"[default {default_lang}]: ").strip()
    if lang_choice and lang_choice.isdigit():
        keys = list(SUPPORTED_LANGS.keys())
        lang = keys[int(lang_choice) - 1]
    else:
        lang = default_lang

    return {"mode": mode, "type": selected_type, "limit": limit, "lang": lang}


def main():
    parser = argparse.ArgumentParser(description="Advanced anime/manga/games downloader")
    parser.add_argument("--type", choices=["all", "anime", "manga", "games"], default=None)
    parser.add_argument("--mode", choices=["single", "genre"], default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--lang", choices=list(SUPPORTED_LANGS.keys()), default=None)
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--no-prompt", action="store_true")
    args = parser.parse_args()

    detected_lang = detect_system_language()
    if args.lang:
        active_lang = args.lang
    else:
        active_lang = detected_lang

    if not args.no_prompt and args.type is None and args.mode is None and args.limit is None:
        config = interactive_config(active_lang)
        selected_type = config["type"]
        mode = config["mode"]
        limit = config["limit"]
        active_lang = config["lang"]
    else:
        selected_type = args.type or "all"
        mode = args.mode or "single"
        limit = args.limit

    print(TEXT[active_lang]["auto_detected"].format(lang=SUPPORTED_LANGS.get(detected_lang, "English")))

    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    if selected_type == "all":
        selected_types = ["anime", "manga", "games"]
    else:
        selected_types = [selected_type]

    if "games" in selected_types and not os.environ.get("RAWG_API_KEY"):
        print(TEXT[active_lang]["no_games_key"])

    aggregated = []
    for kind in selected_types:
        if kind == "games" and not os.environ.get("RAWG_API_KEY"):
            continue
        print(TEXT[active_lang]["processing"].format(type=kind.upper()))
        results = process_one_kind(kind, output_root, mode, limit, resume=True, lang=active_lang)
        aggregated.extend(results)

    metadata_path = output_root / "metadata_advanced.json"
    metadata_path.write_text(json.dumps(aggregated, ensure_ascii=False, indent=2), encoding="utf-8")
    print(TEXT[active_lang]["done"].format(count=len(aggregated)))
    print(TEXT[active_lang]["metadata"].format(path=metadata_path))

    if args.no_prompt:
        return
    input(TEXT[active_lang]["exit_prompt"])


if __name__ == "__main__":
    main()
