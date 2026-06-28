import time
from fastapi import APIRouter, Query
from backend.database import fetch_rows
from backend.models import Transaction

router = APIRouter()


@router.get("")
async def offset_pagination(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):

    count_query = f"SELECT COUNT(*) FROM {Transaction.__tablename__}"
    
    offset = (page - 1) * limit

    query = f"""
        SELECT * FROM {Transaction.__tablename__} 
        ORDER BY created_at DESC 
        LIMIT $1
        OFFSET $2
    """
    
    start = time.perf_counter()
    items = await fetch_rows(query, (limit, offset))
    query_time_ms = round((time.perf_counter() - start) * 1000, 2)

    count_result = await fetch_rows(count_query)
    total_count = count_result[0]["count"]
    total_pages = -(-total_count // limit)

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "query_time_ms": query_time_ms,
        "pagination_type": "offset",
    }
