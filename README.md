# Anime Poster Downloader

Questo repository contiene 4 versioni di uno script Python per scaricare immagini legate ai contenuti anime e affini.

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
   - supporta anime, manga e videogiochi a tema anime/manga
   - permette di interrompere con `Ctrl+C`
   - supporta limiti `--limit`
   - supporta `--resume` e `--update`
   - salva in cartelle separate per tipo

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
python scripts/04_multimedia_downloader.py --type anime --limit 200
python scripts/04_multimedia_downloader.py --type manga --limit 200 --resume
python scripts/04_multimedia_downloader.py --type games --limit 200 --update
```

## Script 04: opzioni principali

```bash
python scripts/04_multimedia_downloader.py --help
```

Opzioni utili:
- `--type anime`
- `--type manga`
- `--type games`
- `--limit 200` per fermarsi dopo N download
- `--resume` per saltare i file già presenti
- `--update` per aggiornare solo contenuti nuovi/nuovi file
- `--output-dir output` per cambiare cartella di destinazione

## Nota

I poster sono recuperati da AniList usando l'API GraphQL per gli anime. Per manga e giochi si usano risorse pubbliche e API accessibili, con gestione degli errori e chiusura controllata. Il downloader supporta arresti manuali tramite `Ctrl+C`.
