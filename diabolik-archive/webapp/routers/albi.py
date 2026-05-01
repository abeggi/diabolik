from fastapi import APIRouter, Query, HTTPException

try:
    from ..database import search_albi, get_albo_detail, get_distinct_years, get_distinct_autori, get_adjacent_albi
except ImportError:
    from database import search_albi, get_albo_detail, get_distinct_years, get_distinct_autori, get_adjacent_albi

router = APIRouter(prefix="/api/albi", tags=["albi"])


@router.get("")
def api_albi(
    q: str = Query(None, description="Cerca per titolo"),
    anno: str = Query(None, description="Filtra per anno"),
    autore: str = Query(None, description="Cerca in soggetto, sceneggiatura, matita, copertinista"),
    sinossi: str = Query(None, description="Cerca nel testo della sinossi"),
    preferito: str = Query(None, description="1 per soli preferiti"),
    tag: str = Query(None, description="Filtra per nome tag"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    order: str = Query("desc", description="asc o desc"),
):
    """Ricerca albi con filtri opzionali."""
    results, total = search_albi(
        q=q,
        anno=anno,
        autore=autore,
        sinossi=sinossi,
        preferito=preferito,
        tag=tag,
        limit=limit,
        offset=offset,
        order=order,
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": results,
    }


@router.get("/{slug}")
def api_albo_detail(slug: str):
    """Dettaglio di un singolo albo."""
    data = get_albo_detail(slug)
    if not data:
        raise HTTPException(status_code=404, detail="Albo non trovato")
    return data


@router.get("/filters/years")
def api_years():
    """Lista anni distinti per il filtro select."""
    return get_distinct_years()


@router.get("/filters/autori")
def api_autori(q: str = Query(None)):
    """Lista autori distinti per l'autocomplete."""
    return get_distinct_autori(q)


@router.get("/{slug}/adjacent")
def api_adjacent(slug: str):
    """Albi adiacenti cronologicamente."""
    data = get_adjacent_albi(slug)
    if data is None:
        raise HTTPException(status_code=404, detail="Albo non trovato")
    return data
