import logging
import random
import sys
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from config import (
    BASE_URL,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    RETRY_BACKOFF,
    SLEEP_MAX,
    SLEEP_MIN,
    TEST_LIMIT,
    USER_AGENT,
)
from db import get_last_ok_albo_slug, init_db, insert_albo, log_scrape, slug_exists
from downloader import download_cover
from parser import parse_albo

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


def fetch_url(url: str) -> Optional[str]:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = SESSION.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            logger.warning(
                "Tentativo %d/%d fallito per %s: %s", attempt, MAX_RETRIES, url, e
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF**attempt)
    return None


def collect_slugs() -> list[str]:
    logger.info("Raccolta elenco albi Inedito dal server...")
    slugs = []

    html = fetch_url(f"{BASE_URL}/index.php/home/getAnnate?t=ine")
    if not html:
        logger.error("Impossibile recuperare l'elenco delle annate.")
        return slugs

    soup = BeautifulSoup(html, "lxml")
    annate = [opt["value"] for opt in soup.find_all("option") if opt.get("value")]
    annate.reverse()

    for annata in annate:
        time.sleep(random.uniform(0.5, 1.0))
        html = fetch_url(f"{BASE_URL}/index.php/home/getTitoli?a={annata}")
        if not html:
            logger.warning("Saltata annata %s (fetch fallito)", annata)
            continue

        soup = BeautifulSoup(html, "lxml")
        for opt in soup.find_all("option"):
            value = opt.get("value")
            if value:
                slugs.append(value)

    logger.info("Trovati %d slug totali.", len(slugs))
    return slugs


def process_slug(slug: str) -> tuple[str, Optional[str], Optional[str], bool, bool]:

    html = fetch_url(f"{BASE_URL}/albo/{slug}/")
    if not html:
        return "error", None, None, False, False

    data = parse_albo(html, slug)
    if not data:
        return "error", None, None, False, False

    data.pop("next_slug", None)
    data.pop("tipo_testo", "")

    had_url = bool(data.get("copertina_url"))
    cover_path, cover_existed = download_cover(
        data["copertina_url"],
        str(data["anno_numerico"]) if data["anno_numerico"] else None,
        slug,
    )
    if cover_path:
        data["copertina_locale"] = cover_path

    insert_albo(data)
    log_scrape(slug, "ok", "")

    anno_label = data["anno_numerico"] or "????"
    num_label = data["numero_inedito"] or "?"
    label = f"{anno_label} #{num_label}"
    return "ok", label, data["titolo"], had_url and not cover_existed, cover_existed


def run(test_mode: bool = False):
    init_db()

    slugs = collect_slugs()
    if not slugs:
        logger.error("Nessuno slug raccolto. Fine.")
        return

    last_slug = get_last_ok_albo_slug()
    start_index = 0
    if last_slug:
        try:
            start_index = slugs.index(last_slug) + 1
            logger.info("Resume: riprendo dopo %s (indice %d)", last_slug, start_index)
        except ValueError:
            logger.info("Resume: slug precedente non trovato nella lista, parto da 0")

    max_albi = TEST_LIMIT if test_mode else None
    processed = 0
    inediti_saved = 0
    skipped_db = 0
    errors = 0
    covers_downloaded = 0
    covers_existing = 0

    for i in range(start_index, len(slugs)):
        slug = slugs[i]

        if max_albi is not None and processed >= max_albi:
            logger.info("Limite test (%d albi) raggiunto. Stop.", max_albi)
            break

        if slug_exists(slug):
            processed += 1
            skipped_db += 1
            logger.info("[skip] %s → già in DB", slug)
            continue

        result, label, titolo, cover_new, cover_exist = process_slug(slug)

        if result == "ok":
            inediti_saved += 1
            processed += 1
            if cover_new:
                covers_downloaded += 1
            if cover_exist:
                covers_existing += 1
            logger.info("[%s] %s → ok", label, titolo)
        else:
            errors += 1
            processed += 1
            logger.info("[error] %s → fetch/parse fallito", slug)

        if processed % 50 == 0 and processed > 0:
            logger.info(
                "--- Progresso: %d/%d processati, %d salvati, %d errori ---",
                processed,
                len(slugs),
                inediti_saved,
                errors,
            )

        time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))

    logger.info("=" * 40)
    logger.info("COMPLETATO")
    logger.info("Albi processati: %d", processed)
    logger.info("Inediti salvati: %d", inediti_saved)
    logger.info("Saltati (gia in DB): %d", skipped_db)
    logger.info("Errori: %d", errors)
    logger.info("Copertine scaricate: %d", covers_downloaded)
    logger.info("Già presenti: %d", covers_existing)


if __name__ == "__main__":
    test_mode = "--test" in sys.argv
    run(test_mode=test_mode)
