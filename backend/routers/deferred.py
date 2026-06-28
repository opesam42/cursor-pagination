import time
from fastapi import APIRouter, Query
from ..database import fetch_rows
from ..models import Transaction

router = APIRouter()


@router.get("")
async def deferred_pagination(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    offset = (page - 1) * limit

    count_query = f"SELECT COUNT(*) FROM {Transaction.__tablename__}"

    deferred_query = f"""
        SELECT main.*
        FROM {Transaction.__tablename__} AS main
        INNER JOIN (
            SELECT id
            FROM {Transaction.__tablename__}
            ORDER BY id DESC
            LIMIT $1
            OFFSET $2
        ) AS skinny
        ON main.id = skinny.id
        ORDER BY main.id DESC
    """

    # Count outside timer — same as offset endpoint
    count_result = await fetch_rows(count_query)
    total_count = count_result[0]["count"]
    total_pages = -(-total_count // limit)

    start = time.perf_counter()
    items = await fetch_rows(deferred_query, (limit, offset))
    query_time_ms = round((time.perf_counter() - start) * 1000, 2)

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_more": len(items) == limit,
        "query_time_ms": query_time_ms,
        "pagination_type": "deferred_join",
    }
