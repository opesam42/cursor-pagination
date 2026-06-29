import time
from fastapi import APIRouter, Query
from backend.database import fetch_rows
from backend.models import Transaction

router = APIRouter()


@router.get("")
async def cursor_pagination(cursor: int | None = Query(default=None), limit: int = Query(20, ge=1, le=100)):
    if cursor is None:
        query = f"""
            SELECT * FROM {Transaction.__tablename__}
            ORDER BY id DESC
            LIMIT $1
        """
        params = (limit,)
    else:
        query = f"""
            SELECT * FROM {Transaction.__tablename__}
            WHERE id < $1
            ORDER BY id DESC
            LIMIT $2
        """
        params = (cursor, limit)

    start = time.perf_counter()
    items = await fetch_rows(query, params)
    query_time_ms = round((time.perf_counter() - start) * 1000, 2)

    # get the next cursor which is the id of the last item returned
    if items:
        next_cursor = items[-1]["id"]
    else:
        next_cursor = None


    return {
        "items": items,
        "next_cursor": next_cursor,
        "has_more": len(items) == limit,
        "query_time_ms": query_time_ms,
        "pagination_type": "cursor",
    }


@router.get("/benchmark")
async def cursor_benchmark(depths: str = Query(...), limit: int = Query(20, ge=1, le=100)):
    # Real cursor pagination can only walk forward step by step — no jumping to a page.
    # Walking that out one HTTP round-trip per step would mean tens of thousands of
    # requests to reach deep pages. Instead we derive the boundary id arithmetically:
    # id is a gap-free BIGSERIAL (seed.py only ever inserts sequentially, never deletes),
    # so the id at the start of page P is just max_id - (P - 1) * limit. We still run the
    # real WHERE id < boundary cursor query and time it for real — only the boundary
    # lookup is skipped, not the benchmark itself.
    target_pages = sorted({int(d) for d in depths.split(",") if d.strip()})

    max_id_result = await fetch_rows(f"SELECT MAX(id) AS max_id FROM {Transaction.__tablename__}")
    max_id = max_id_result[0]["max_id"] or 0

    timings: dict[int, float] = {}

    for page in target_pages:
        boundary_id = max_id - (page - 1) * limit

        if boundary_id >= max_id:
            query = f"""
                SELECT id FROM {Transaction.__tablename__}
                ORDER BY id DESC
                LIMIT $1
            """
            params = (limit,)
        else:
            query = f"""
                SELECT id FROM {Transaction.__tablename__}
                WHERE id <= $1
                ORDER BY id DESC
                LIMIT $2
            """
            params = (boundary_id, limit)

        start = time.perf_counter()
        await fetch_rows(query, params)
        timings[page] = round((time.perf_counter() - start) * 1000, 2)

    return {
        "timings": timings,
        "pagination_type": "cursor",
    }
