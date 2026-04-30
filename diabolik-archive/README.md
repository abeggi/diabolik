# Diabolik Archive Scraper

Archivio locale degli albi **Diabolik Inedito** dal sito ufficiale [diabolik.it](https://www.diabolik.it).

## Struttura

```
diabolik-archive/
├── scraper.py         # logica principale
├── db.py              # gestione SQLite
├── parser.py          # parsing HTML
├── downloader.py      # download immagini
├── config.py          # costanti
├── requirements.txt   # dipendenze
├── diabolik.db        # generato a runtime
└── covers/            # covers/ANNO/slug.jpg
```

## Requisiti

- Python 3.10+
- Dipendenze: `requests`, `beautifulsoup4`, `lxml`

## Installazione

```bash
cd diabolik-archive
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Utilizzo

```bash
# Traversal completo (dal 1962 a oggi)
.venv/bin/python scraper.py

# Test primi 5 albi
.venv/bin/python scraper.py --test
```

## Funzionamento

1. Parte dal primo albo Inedito (1962) e segue i link "albo successivo"
2. Salta automaticamente albi non-Inedito (Fuori Serie, Grande Diabolik, Magnum, DK)
3. Salta albi già presenti nel DB senza riscaricare nulla
4. In caso di interruzione, riprende dall'ultimo albo processato
5. Rate limiting: 1-2 secondi random tra le richieste
6. Retry automatico (max 3 tentativi con backoff esponenziale)

## Output a terminale

```
[1962 #1] Il re del terrore → ok
[1963 #2] L'inafferrabile criminale → ok
[1963 #3] L'arresto di Diabolik → ok
[1962 #4] Atroce vendetta → ok
...
========================================
COMPLETATO
Albi processati: 923
Inediti salvati: 921
Skippati (non inedito): 2
Errori: 0
Copertine scaricate: 891
Già presenti: 30
```

## Database

Tabelle: `albi` (metadati + path copertina) e `scrape_log` (storico operazioni).

Le copertine sono salvate in `covers/ANNO/slug.jpg`.
