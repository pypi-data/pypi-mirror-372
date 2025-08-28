from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi import Query
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from sqlalchemy import desc
from sqlalchemy.orm import Session

from fastpluggy.core.auth import require_authentication
from fastpluggy.core.database import get_db
from ..models import ScheduledQuery
from ..models import ScheduledQueryResultHistory
from ..tasks import execute_scheduled_query

api_router = APIRouter(
    prefix="/api",
    dependencies=[Depends(require_authentication)]
)

@api_router.get("/run-now/{query_id}")
async def run_scheduled_query_now(
        query_id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    """
    Run a scheduled query immediately and redirect back to the queries list.
    """
    # Check if the query exists
    query = db.query(ScheduledQuery).filter(ScheduledQuery.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail=f"Scheduled query with ID {query_id} not found")

    # Execute the query asynchronously
    await execute_scheduled_query(query_id)

    # Redirect back to the scheduled queries list
    return RedirectResponse(url=str(request.url_for("read_scheduled_queries")), status_code=303)


@api_router.get("/execution-history/{query_id}", name="get_execution_history")
def get_execution_history(
        query_id: int,
        page: int = Query(1, ge=1, description="Page number (1-based)"),
        limit: int = Query(50, ge=1, le=200, description="Number of records per page"),
        status_filter: str = Query("all", description="Filter by status: all, success, failed, timeout"),
        db: Session = Depends(get_db)
):
    """
    Get execution history for a specific scheduled query with pagination and filtering.
    """
    # Verify the query exists
    scheduled_query = db.query(ScheduledQuery).filter(ScheduledQuery.id == query_id).first()
    if not scheduled_query:
        return JSONResponse(
            status_code=404,
            content={"error": f"Scheduled query with ID {query_id} not found"}
        )

    # Build the base query
    history_query = db.query(ScheduledQueryResultHistory).filter(
        ScheduledQueryResultHistory.scheduled_query_id == query_id
    )

    # Apply status filter if specified
    if status_filter != "all":
        history_query = history_query.filter(ScheduledQueryResultHistory.status == status_filter)

    # Order by executed_at descending (most recent first) and apply pagination
    history_query = history_query.order_by(desc(ScheduledQueryResultHistory.executed_at))

    # Get total count for pagination info
    total_count = history_query.count()

    # Apply pagination
    offset = (page - 1) * limit
    history_records = history_query.offset(offset).limit(limit).all()

    # Convert to JSON-serializable format
    history_data = []
    for record in history_records:
        history_data.append({
            "id": record.id,
            "executed_at": record.executed_at.strftime('%Y-%m-%d %H:%M:%S') if record.executed_at else None,
            "duration_ms": record.duration_ms,
            "result": record.result,
            "status": record.status,
            "error_message": record.error_message,
            "grafana_metrics_snapshot": record.grafana_metrics_snapshot
        })

    # Calculate pagination info
    total_pages = (total_count + limit - 1) // limit  # Ceiling division
    has_next = page < total_pages
    has_prev = page > 1

    return JSONResponse(content={
        "data": history_data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        },
        "query_info": {
            "id": scheduled_query.id,
            "name": scheduled_query.name
        }
    })
