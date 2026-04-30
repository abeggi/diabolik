import re
from typing import Optional

from bs4 import BeautifulSoup, Tag

from config import BASE_URL, NON_INEDITO_KEYWORDS


def parse_albo(html: str, slug: str) -> Optional[dict]:
    soup = BeautifulSoup(html, "lxml")

    title_cro = soup.select_one("div.titleCro")
    if not title_cro:
        return None

    h1 = title_cro.find("h1")
    titolo = h1.get_text(strip=True) if h1 else None

    h4 = title_cro.find("h4")
    tipo_testo = h4.get_text(strip=True) if h4 else ""

    if not is_inedito(tipo_testo):
        return None

    meta = _parse_metadata(soup)
    sinossi = _parse_sinossi(soup)
    copertina_url = _parse_copertina_url(soup)
    next_slug = _parse_next_slug(soup)

    anno_str = meta.get("Anno", "")
    anno_numerico = _parse_anno_numerico(anno_str)

    numero_pagine = _parse_int(meta.get("Numero pagine", ""))
    numero_inedito = _parse_int(meta.get("Inedito n.", ""))

    mese = _parse_mese(tipo_testo, meta)

    return {
        "slug": slug,
        "titolo": titolo,
        "numero_inedito": numero_inedito,
        "anno": anno_str,
        "anno_numerico": anno_numerico,
        "mese": mese,
        "numero_pagine": numero_pagine,
        "soggetto": meta.get("Soggetto"),
        "sceneggiatura": meta.get("Sceneggiatura"),
        "matita": meta.get("Matita") or meta.get("Matite"),
        "chine": meta.get("Chine"),
        "lettering": meta.get("Lettering"),
        "retini": meta.get("Retini"),
        "copertinista": meta.get("Copertina"),
        "sinossi": sinossi,
        "copertina_url": copertina_url,
        "copertina_locale": None,
        "url_pagina": f"{BASE_URL}/albo/{slug}/",
        "tipo_testo": tipo_testo,
        "next_slug": next_slug,
    }


def is_inedito(tipo_testo: str) -> bool:
    for kw in NON_INEDITO_KEYWORDS:
        if kw.lower() in tipo_testo.lower():
            return False
    return True


def _parse_metadata(soup: BeautifulSoup) -> dict:
    section = soup.select_one("#innerCroOne")
    if not section:
        return {}

    first_p = section.select_one(".col-md-5 p, .col-md-5 p")
    if not first_p:
        first_p = section.find("p")

    if not first_p:
        return {}

    meta = {}
    text = str(first_p)

    for match in re.finditer(
        r"<b>(?P<key>[^<]+):?</b>\s*(?P<value>.*?)(?:<br\s*/?>|$)", text
    ):
        key = match.group("key").strip().rstrip(":")
        value = BeautifulSoup(match.group("value"), "lxml").get_text(strip=True)
        if value:
            meta[key] = value

    return meta


def _parse_sinossi(soup: BeautifulSoup) -> Optional[str]:
    section = soup.select_one("#innerCroOne")
    if not section:
        return None

    hr = section.find("hr")
    if not hr:
        return None

    p = hr.find_next_sibling("p")
    if p and "mt-3" in p.get("class", []):
        return p.get_text(strip=True)
    return None


def _parse_copertina_url(soup: BeautifulSoup) -> Optional[str]:
    section = soup.select_one("#innerCroOne")
    if not section:
        return None

    for img in section.find_all("img"):
        alt = img.get("alt", "")
        if "copertina" in alt.lower():
            src = img.get("src", "")
            if src.startswith("/"):
                src = BASE_URL + src
            return src
    return None


def _parse_next_slug(soup: BeautifulSoup) -> Optional[str]:
    next_link = soup.select_one(
        "#prevNextAlbo .border-left a[title*='successivo']"
    )
    if not next_link:
        return None
    href = next_link.get("href", "")
    match = re.search(r"/albo/([^/]+)/?", href)
    if match:
        return match.group(1)
    return None


def _parse_anno_numerico(anno_str: str) -> Optional[int]:
    if not anno_str:
        return None
    match = re.search(r"(\d{4})", anno_str)
    return int(match.group(1)) if match else None


def _parse_int(text: str) -> Optional[int]:
    if not text:
        return None
    match = re.search(r"(\d+)", str(text))
    return int(match.group(1)) if match else None


def _parse_mese(tipo_testo: str, meta: dict) -> Optional[str]:
    mese_from_meta = meta.get("Mese")
    if mese_from_meta:
        return mese_from_meta

    match = re.search(
        r"(Gennaio|Febbraio|Marzo|Aprile|Maggio|Giugno|"
        r"Luglio|Agosto|Settembre|Ottobre|Novembre|Dicembre)",
        tipo_testo,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)

    return None
