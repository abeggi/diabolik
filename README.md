# Diabolik Archive

Archivio locale degli albi **Diabolik Inedito** da [diabolik.it](https://www.diabolik.it).
Include scraper e interfaccia web di consultazione.

## Struttura

```
.
├── diabolik-archive/
│   ├── scraper.py              # scarica albi e copertine
│   ├── db.py                   # schema e query SQLite
│   ├── parser.py               # parsing HTML pagine albo
│   ├── downloader.py           # download copertine
│   ├── config.py               # costanti e URL
│   ├── diabolik.db             # SQLite generato a runtime
│   ├── covers/                 # covers/ANNO/slug.jpg
│   └── webapp/
│       ├── main.py             # FastAPI, porta 8080
│       ├── database.py         # query webapp
│       ├── routers/
│       │   ├── albi.py         # ricerca e dettaglio
│       │   ├── userdata.py     # preferiti, note, tag
│       │   └── settings.py     # refresh, backup
│       └── static/
│           ├── index.html      # ricerca + grid
│           ├── albo.html       # dettaglio albo
│           ├── settings.html   # impostazioni
│           ├── style.css       # tema chiaro/scuro
│           └── app.js          # JS condiviso
├── diabolik-archive.service    # unità systemd
└── service.sh                  # script gestione servizio
```

## Requisiti

- Python 3.10+
- Dipendenze in `requirements.txt`

## Installazione

```bash
cd diabolik-archive
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Scraper

```bash
cd diabolik-archive

# Scarica tutti gli albi
.venv/bin/python scraper.py

# Test primi 5
.venv/bin/python scraper.py --test
```

Riprende automaticamente dall'ultimo albo processato. Rate limiting 1-2s tra richieste, retry automatico.

## Webapp

```bash
cd diabolik-archive/webapp
.venv/bin/python main.py
# oppure: uvicorn main:app --host 0.0.0.0 --port 8080
```

Apri `http://localhost:8080`.

Funzionalità:
- Ricerca full-text, filtro per anno, autore, tag, preferiti
- Dettaglio albo con metadati, sinossi, copertina
- Preferiti ★, note personali, tag con autocompletamento
- Ordinamento crescente/decrescente
- Tema chiaro/scuro
- Impostazioni: statistiche, refresh albi

## Docker

```bash
# Build (dalla root del repo)
docker build -t abeggi/diabolik-archive .

# Avvio
docker compose up -d

# Push su Docker Hub
docker push abeggi/diabolik-archive:latest
```

Volumi montati: `diabolik.db` e `covers/` persistono sull'host.

## Servizio systemd

```bash
sudo ./service.sh install      # installa e avvia
sudo ./service.sh uninstall    # ferma e rimuove
sudo ./service.sh start|stop|restart|status
```

## Database

Tabelle: `albi` (metadati), `scrape_log` (storico), `user_data` (preferiti e note), `tags` e `albi_tags` (tag N:N).
SQLite in `diabolik-archive/diabolik.db`.
