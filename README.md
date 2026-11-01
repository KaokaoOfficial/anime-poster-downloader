# Anime Poster Downloader

Questo repository contiene 3 versioni di uno script Python per scaricare poster di anime da AniList.

## Versioni disponibili

1. `scripts/01_basic_download.py`
   - download semplice
   - salva i poster in una cartella unica

2. `scripts/02_foldered_download.py`
   - salva i poster in sotto-cartelle organizzate per genere

3. `scripts/03_multiprocessing_dataset.py`
   - usa `multiprocessing` per velocizzare il download
   - crea una struttura pronta per dataset `train/val/test`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# oppure .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Esecuzione

```bash
python scripts/01_basic_download.py
python scripts/02_foldered_download.py
python scripts/03_multiprocessing_dataset.py
```

## Nota

I poster sono recuperati da AniList usando l'API GraphQL. Per evitare rate limit, i script includono piccoli ritardi e gestione errori.
