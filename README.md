# Anime Poster Downloader

Questo repository contiene una raccolta di script Python per scaricare immagini legate a anime, manga e videogiochi ispirati all'universo anime.

## Versioni disponibili

1. `scripts/01_basic_download.py`
   - download semplice
   - salva i poster in una cartella unica

2. `scripts/02_foldered_download.py`
   - salva i poster in sotto-cartelle organizzate per genere

3. `scripts/03_multiprocessing_dataset.py`
   - usa `multiprocessing` per velocizzare il download
   - crea una struttura pronta per dataset `train/val/test`

4. `scripts/04_multimedia_downloader.py`
   - supporta anime, manga e videogiochi
   - supporta limiti e pause di sicurezza

5. `scripts/05_advanced_multimedia_downloader.py`
   - modalità interattiva avanzata
   - scelta tra cartella unica o per genere
   - scelta tra anime, manga, giochi o tutti insieme
   - scelta del numero di elementi da scaricare
   - selezione lingua con rilevamento automatico del sistema

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# oppure .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Esecuzione

```bash
python scripts/05_advanced_multimedia_downloader.py
```

Oppure in modalità non interattiva:

```bash
python scripts/05_advanced_multimedia_downloader.py --type all --limit 200 --mode genre --lang it
python scripts/05_advanced_multimedia_downloader.py --type anime --limit 100 --mode single --lang en
python scripts/05_advanced_multimedia_downloader.py --type manga --limit 50 --mode genre --lang it
```

## Script 05: opzioni principali

```bash
python scripts/05_advanced_multimedia_downloader.py --help
```

Opzioni utili:
- `--type all|anime|manga|games`
- `--mode single|genre`
- `--limit 200` per fermarsi dopo N elementi per tipo
- `--lang en|it|es|fr|de|ja|ru`
- `--output-dir output`
- `--no-prompt` per usare solo i parametri da riga di comando

## Nota

Per anime e manga si usa AniList. Per i giochi si richiede una chiave RAWG in variabile d'ambiente `RAWG_API_KEY` quando si vuole scaricare contenuti di tipo `games`.
