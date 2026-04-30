import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "diabolik.db")


def _strip_covers_prefix(path):
    if path and path.startswith("covers/"):
        return path[7:]
    return path


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


WEBAPP_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    albo_slug TEXT UNIQUE NOT NULL,
    preferito INTEGER DEFAULT 0,
    note TEXT DEFAULT '',
    FOREIGN KEY (albo_slug) REFERENCES albi(slug)
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS albi_tags (
    albo_slug TEXT NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (albo_slug, tag_id),
    FOREIGN KEY (albo_slug) REFERENCES albi(slug),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
"""


def init_webapp_db():
    conn = get_conn()
    conn.executescript(WEBAPP_SCHEMA)
    conn.commit()
    conn.close()


def search_albi(
    q=None,
    anno=None,
    autore=None,
    preferito=None,
    tag=None,
    limit=50,
    offset=0,
    order="asc",
):
    conn = get_conn()
    conditions = []
    params = []

    if q:
        conditions.append("a.titolo LIKE ?")
        params.append(f"%{q}%")

    if anno:
        conditions.append("a.anno_numerico = ?")
        params.append(int(anno))

    if autore:
        autore_cond = "(a.soggetto LIKE ? OR a.sceneggiatura LIKE ? OR a.matita LIKE ? OR a.copertinista LIKE ?)"
        conditions.append(autore_cond)
        like = f"%{autore}%"
        params.extend([like, like, like, like])

    if preferito is not None and str(preferito) == "1":
        conditions.append("ud.preferito = 1")

    if tag:
        conditions.append(
            "a.slug IN (SELECT at2.albo_slug FROM albi_tags at2 JOIN tags t2 ON at2.tag_id = t2.id WHERE t2.nome = ?)"
        )
        params.append(tag)

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    base_join = "LEFT JOIN user_data ud ON a.slug = ud.albo_slug"

    count_sql = f"SELECT COUNT(*) FROM albi a {base_join} {where}"
    total = conn.execute(count_sql, params).fetchone()[0]

    order_dir = "DESC" if order == "desc" else "ASC"
    sql = f"""
        SELECT a.slug, a.titolo, a.numero_inedito, a.anno, a.copertina_locale,
               ud.preferito, ud.note
        FROM albi a
        {base_join}
        {where}
        ORDER BY a.anno_numerico {order_dir}, a.numero_inedito {order_dir}
        LIMIT ? OFFSET ?
    """
    rows = conn.execute(sql, params + [limit, offset]).fetchall()

    results = []
    for r in rows:
        tags_list = get_tags_for_slug(conn, r["slug"])
        results.append({
            "slug": r["slug"],
            "titolo": r["titolo"],
            "numero_inedito": r["numero_inedito"],
            "anno": r["anno"],
            "copertina_locale": _strip_covers_prefix(r["copertina_locale"]),
            "preferito": bool(r["preferito"]) if r["preferito"] is not None else False,
            "ha_note": bool(r["note"]) if r["note"] is not None else False,
            "tags": tags_list,
        })

    conn.close()
    return results, total


def get_tags_for_slug(conn, slug):
    rows = conn.execute(
        "SELECT t.nome FROM tags t JOIN albi_tags at ON t.id = at.tag_id WHERE at.albo_slug = ? ORDER BY t.nome",
        (slug,),
    ).fetchall()
    return [r["nome"] for r in rows]


def get_albo_detail(slug):
    conn = get_conn()
    row = conn.execute(
        """
        SELECT a.*, ud.preferito, ud.note
        FROM albi a
        LEFT JOIN user_data ud ON a.slug = ud.albo_slug
        WHERE a.slug = ?
        """,
        (slug,),
    ).fetchone()
    if not row:
        conn.close()
        return None

    tags_list = get_tags_for_slug(conn, slug)

    result = dict(row)
    result["copertina_locale"] = _strip_covers_prefix(result.get("copertina_locale"))
    result["preferito"] = bool(result["preferito"]) if result["preferito"] is not None else False
    result["ha_note"] = bool(result["note"]) if result["note"] is not None else False
    result["tags"] = tags_list
    conn.close()
    return result


def toggle_preferito(slug):
    conn = get_conn()
    conn.execute(
        "INSERT INTO user_data (albo_slug, preferito, note) VALUES (?, 1, '') ON CONFLICT(albo_slug) DO UPDATE SET preferito = 1 - preferito",
        (slug,),
    )
    conn.commit()
    row = conn.execute(
        "SELECT preferito FROM user_data WHERE albo_slug = ?", (slug,)
    ).fetchone()
    conn.close()
    return bool(row["preferito"]) if row else False


def save_note(slug, note):
    conn = get_conn()
    conn.execute(
        "INSERT INTO user_data (albo_slug, preferito, note) VALUES (?, 0, ?) ON CONFLICT(albo_slug) DO UPDATE SET note = ?",
        (slug, note, note),
    )
    conn.commit()
    conn.close()


def add_tag(slug, nome):
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO tags (nome) VALUES (?)", (nome,))
    row = conn.execute("SELECT id FROM tags WHERE nome = ?", (nome,)).fetchone()
    tag_id = row["id"]
    conn.execute(
        "INSERT OR IGNORE INTO albi_tags (albo_slug, tag_id) VALUES (?, ?)",
        (slug, tag_id),
    )
    conn.commit()
    conn.close()


def remove_tag(slug, nome):
    conn = get_conn()
    conn.execute(
        "DELETE FROM albi_tags WHERE albo_slug = ? AND tag_id = (SELECT id FROM tags WHERE nome = ?)",
        (slug, nome),
    )
    conn.execute(
        "DELETE FROM tags WHERE id NOT IN (SELECT DISTINCT tag_id FROM albi_tags)"
    )
    conn.commit()
    conn.close()


def get_all_tags():
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT t.nome, COUNT(at.albo_slug) as conteggio
        FROM tags t
        LEFT JOIN albi_tags at ON t.id = at.tag_id
        GROUP BY t.id
        ORDER BY t.nome
        """
    ).fetchall()
    conn.close()
    return [{"nome": r["nome"], "conteggio": r["conteggio"]} for r in rows]


def get_stats():
    conn = get_conn()
    totale = conn.execute("SELECT COUNT(*) FROM albi").fetchone()[0]
    totale_preferiti = conn.execute(
        "SELECT COUNT(*) FROM user_data WHERE preferito = 1"
    ).fetchone()[0]
    ultimo = conn.execute(
        "SELECT scraped_at FROM albi ORDER BY id DESC LIMIT 1"
    ).fetchone()
    ultimo_scrape = ultimo["scraped_at"] if ultimo else None

    db_size = os.path.getsize(DB_PATH)
    db_size_mb = round(db_size / (1024 * 1024), 2)

    conn.close()
    return {
        "totale_albi": totale,
        "totale_preferiti": totale_preferiti,
        "ultimo_scrape": ultimo_scrape,
        "db_size_mb": db_size_mb,
    }


def get_distinct_years():
    conn = get_conn()
    rows = conn.execute(
        "SELECT DISTINCT anno_numerico FROM albi WHERE anno_numerico IS NOT NULL ORDER BY anno_numerico ASC"
    ).fetchall()
    conn.close()
    return [r["anno_numerico"] for r in rows]


def count_albi():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM albi").fetchone()[0]
    conn.close()
    return total


def get_distinct_autori(q=None):
    conn = get_conn()
    fields = ['soggetto', 'sceneggiatura', 'matita', 'copertinista']
    union_parts = [
        f"SELECT {f} AS nome FROM albi WHERE {f} IS NOT NULL AND {f} != ''"
        for f in fields
    ]
    union_sql = " UNION ".join(union_parts)
    if q:
        rows = conn.execute(
            f"SELECT DISTINCT nome FROM ({union_sql}) WHERE nome LIKE ? ORDER BY nome LIMIT 20",
            (f"%{q}%",),
        ).fetchall()
    else:
        rows = conn.execute(
            f"SELECT DISTINCT nome FROM ({union_sql}) ORDER BY nome LIMIT 50"
        ).fetchall()
    conn.close()
    return [r["nome"] for r in rows]


def get_adjacent_albi(slug):
    conn = get_conn()
    current = conn.execute(
        "SELECT anno_numerico, numero_inedito FROM albi WHERE slug = ?", (slug,)
    ).fetchone()
    if not current:
        conn.close()
        return None
    anno = current["anno_numerico"]
    numero = current["numero_inedito"]
    prev_row = conn.execute(
        """SELECT slug, titolo, numero_inedito FROM albi
           WHERE anno_numerico < ? OR (anno_numerico = ? AND numero_inedito < ?)
           ORDER BY anno_numerico DESC, numero_inedito DESC LIMIT 1""",
        (anno, anno, numero),
    ).fetchone()
    next_row = conn.execute(
        """SELECT slug, titolo, numero_inedito FROM albi
           WHERE anno_numerico > ? OR (anno_numerico = ? AND numero_inedito > ?)
           ORDER BY anno_numerico ASC, numero_inedito ASC LIMIT 1""",
        (anno, anno, numero),
    ).fetchone()
    conn.close()
    return {
        "prev": {"slug": prev_row["slug"], "titolo": prev_row["titolo"], "numero": prev_row["numero_inedito"]} if prev_row else None,
        "next": {"slug": next_row["slug"], "titolo": next_row["titolo"], "numero": next_row["numero_inedito"]} if next_row else None,
    }
