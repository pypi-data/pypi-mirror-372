
from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from fastpluggy.core.auth import require_authentication
from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_view_builder
from fastpluggy.core.menu.decorator import menu_entry
from fastpluggy.core.view_builer.components.table_model import TableModelView
from fastpluggy.core.widgets import CustomTemplateWidget
from fastpluggy.core.widgets.render_field_tools import RenderFieldTools
from ..models import ScheduledQuery

crud_router = APIRouter(
    dependencies=[Depends(require_authentication)]
)


@menu_entry(label="Scheduled Queries", icon="fa fa-clock")
@crud_router.get("/")
def read_scheduled_queries(
        request: Request,
        db: Session = Depends(get_db),
        view_builder=Depends(get_view_builder)
):
    """
    Retrieve a list of scheduled queries.
    """
    items = [
        TableModelView(
            model=ScheduledQuery,
            fields=['id', 'name', 'query', 'last_executed', 'cron_schedule', 'enabled', 'last_result'],
            field_callbacks={
                ScheduledQuery.query: lambda query: query[:50] + '...' if query else None,
                ScheduledQuery.enabled: RenderFieldTools.render_boolean
            },
            links=[
                {
                    "url": str(request.url_for("edit_scheduled_query_form", query_id='<id>')),
                    "label": "Edit",
                    "icon": "fa fa-edit",
                    "class": "btn btn-sm btn-secondary"
                },
                {
                    "url": str(request.url_for("run_scheduled_query_now", query_id='<id>')),
                    "label": "Run Now",
                    "icon": "fa fa-play",
                    "class": "btn btn-sm btn-primary"
                }
            ]
        )
    ]
    return view_builder.generate(
        request,
        widgets=items,
        title='Scheduled Queries',
    )
@crud_router.get("/edit/{query_id}")
def edit_scheduled_query_form(
        query_id: int,
        request: Request,
        db: Session = Depends(get_db),
        view_builder=Depends(get_view_builder)
):
    """
    Show the edit form for a scheduled query.
    """
    # Get the query to edit
    query = db.query(ScheduledQuery).filter(ScheduledQuery.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail=f"Scheduled query with ID {query_id} not found")

    items = [
        CustomTemplateWidget(
            template_name="scheduled_query/edit_form.html.j2",
            context={
                "request": request,
                "query": query,
                "form_action": str(request.url_for("update_scheduled_query", query_id=query_id))
            }
        )
    ]

    return view_builder.generate(
        request,
        widgets=items,
        title=f'Edit Query: {query.name}',
    )


@crud_router.post("/edit/{query_id}")
def update_scheduled_query(
        query_id: int,
        request: Request,
        db: Session = Depends(get_db),
        name: str = Form(...),
        query: str = Form(...),
        cron_schedule: str = Form(...),
        enabled: bool = Form(False),
        render_type: str = Form("auto")
):
    """
    Update a scheduled query with form data.
    """
    # Get the query to update
    scheduled_query = db.query(ScheduledQuery).filter(ScheduledQuery.id == query_id).first()
    if not scheduled_query:
        raise HTTPException(status_code=404, detail=f"Scheduled query with ID {query_id} not found")

    # Update the query fields
    scheduled_query.name = name
    scheduled_query.query = query
    scheduled_query.cron_schedule = cron_schedule
    scheduled_query.enabled = enabled
    scheduled_query.render_type = render_type

    # Save changes
    db.commit()

    # Redirect back to the scheduled queries list
    return RedirectResponse(url=str(request.url_for("read_scheduled_queries")), status_code=303)
