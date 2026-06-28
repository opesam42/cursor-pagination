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
            ORDER BY created_at DESC
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
