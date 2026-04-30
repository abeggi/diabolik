import sqlite3
import os

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS albi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    titolo TEXT,
    numero_inedito INTEGER,
    anno TEXT,
    anno_numerico INTEGER,
    mese TEXT,
    numero_pagine INTEGER,
    soggetto TEXT,
    sceneggiatura TEXT,
    matita TEXT,
    chine TEXT,
    lettering TEXT,
    retini TEXT,
    copertinista TEXT,
    sinossi TEXT,
    copertina_url TEXT,
    copertina_locale TEXT,
    url_pagina TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scrape_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT,
    status TEXT,
    messaggio TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def insert_albo(data: dict):
    conn = get_conn()
    conn.execute(
        """
        INSERT OR REPLACE INTO albi (
            slug, titolo, numero_inedito, anno, anno_numerico, mese,
            numero_pagine, soggetto, sceneggiatura, matita, chine,
            lettering, retini, copertinista, sinossi,
            copertina_url, copertina_locale, url_pagina
        ) VALUES (
            :slug, :titolo, :numero_inedito, :anno, :anno_numerico, :mese,
            :numero_pagine, :soggetto, :sceneggiatura, :matita, :chine,
            :lettering, :retini, :copertinista, :sinossi,
            :copertina_url, :copertina_locale, :url_pagina
        )
        """,
        data,
    )
    conn.commit()
    conn.close()


def slug_exists(slug: str) -> bool:
    conn = get_conn()
    row = conn.execute("SELECT 1 FROM albi WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    return row is not None


def get_last_ok_slug() -> str | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT slug FROM scrape_log WHERE status = 'ok' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return row["slug"] if row else None


def get_last_ok_albo_slug() -> str | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT slug FROM albi ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return row["slug"] if row else None


def log_scrape(slug: str, status: str, message: str = ""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO scrape_log (slug, status, messaggio) VALUES (?, ?, ?)",
        (slug, status, message),
    )
    conn.commit()
    conn.close()
