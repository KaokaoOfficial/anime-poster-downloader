# Anime Poster Downloader

This repository contains a collection of Python scripts designed to download images related to anime, manga, and anime-inspired video games.

## Available Versions

1. `scripts/01_basic_download.py`
   - simple download
   - saves posters to a single folder

2. `scripts/02_foldered_download.py`
   - saves posters into subfolders organized by genre

3. `scripts/03_multiprocessing_dataset.py`
   - uses `multiprocessing` to speed up downloads
   - creates a ready-to-use `train/val/test` dataset structure

4. `scripts/04_multimedia_downloader.py`
   - supports anime, manga, and video games
   - features download limits and rate-limiting delays

5. `scripts/05_advanced_multimedia_downloader.py`
   - advanced interactive mode
   - option to choose between a single folder or genre-based organization
   - option to select anime, manga, games, or all combined
   - configurable download limit per media type
   - language selection with automatic system language detection

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Running the Script

```bash
python scripts/05_advanced_multimedia_downloader.py
```

Or run in non-interactive mode:

```bash
python scripts/05_advanced_multimedia_downloader.py --type all --limit 200 --mode genre --lang it
python scripts/05_advanced_multimedia_downloader.py --type anime --limit 100 --mode single --lang en
python scripts/05_advanced_multimedia_downloader.py --type manga --limit 50 --mode genre --lang it
```

## Script 05: Core Options

```bash
python scripts/05_advanced_multimedia_downloader.py --help
```

Key options:
- `--type all|anime|manga|games`
- `--mode single|genre`
- `--limit 200` stops after downloading N items per type
- `--lang en|it|es|fr|de|ja|ru`
- `--output-dir output`
- `--no-prompt` relies strictly on command-line arguments

## Note

Anime and manga data are fetched via AniList. To download `games`, you'll need a RAWG API key set in your `RAWG_API_KEY` environment variable.
