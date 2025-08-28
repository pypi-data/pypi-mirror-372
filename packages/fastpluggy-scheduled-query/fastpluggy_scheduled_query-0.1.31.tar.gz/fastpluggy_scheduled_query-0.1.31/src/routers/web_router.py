from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, selectinload

from fastpluggy.core.auth import require_authentication
from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_view_builder
from fastpluggy.core.menu.decorator import menu_entry
from fastpluggy.core.view_builer.components.table_model import TableModelView
from fastpluggy.core.widgets import CustomTemplateWidget
from fastpluggy.core.widgets.categories.data.raw import RawWidget
from fastpluggy.core.widgets.render_field_tools import RenderFieldTools
from fastpluggy_plugin.ui_tools.extra_widget.layout.grid import GridWidget
from ..models import ScheduledQuery
from ..tasks import execute_scheduled_query
from ..widgets.scheduled_query_result_widget import ScheduledQueryResultWidget

web_router = APIRouter(
    dependencies=[Depends(require_authentication)]
)



@menu_entry(label="Cards", icon="fa fa-th")
@web_router.get("/cards")
def read_scheduled_queries_cards(
        request: Request,
        db: Session = Depends(get_db),
        view_builder=Depends(get_view_builder)
):
    """
    Retrieve a list of scheduled queries in card format.
    """

    all_queries = (
        db.query(ScheduledQuery).where(ScheduledQuery.enabled == True)
        .options(selectinload(ScheduledQuery.execution_history))
        .all()
    )

    widgets = []
    for q in all_queries:
        widgets.append({
            "type": "custom",
            "template": "scheduled_query/scheduled_query_card.html.j2",
            "context": {"scheduled_query": q, "request": request}
        })

    items = [
        GridWidget.create_responsive_grid(
            widgets=widgets,
            cols_sm=1,
            cols_md=6,
            cols_lg=6,
            cols_xl=6,
        ),
    ]
    return view_builder.generate(
        request,
        widgets=items,
        title='Scheduled Queries',
    )


@menu_entry(label="Dashboard", icon="fa fa-dashboard", position=0)
@web_router.get("/dashboard")
def dashboard(
        request: Request,
        db: Session = Depends(get_db),
        view_builder=Depends(get_view_builder)
):
    """
    Render the Query Results Dashboard with scheduled queries (without execution history for performance).
    """
    # Fetch only scheduled queries without execution history for better performance
    scheduled_queries = db.query(ScheduledQuery).all()

    # Generate the API URL for execution history using url_for
    api_execution_history_url = str(request.url_for("get_execution_history", query_id="QUERY_ID_PLACEHOLDER"))

    items = [
        CustomTemplateWidget(
            template_name="scheduled_query/dashboard.html.j2",
            context={
                "request": request,
                "scheduled_queries": scheduled_queries,
                "api_execution_history_url": api_execution_history_url
            }
        )
    ]

    return view_builder.generate(
        request,
        widgets=items,
    )



@menu_entry(label="Results Widgets", icon="fa fa-th")
@web_router.get("/results-widgets")
def results_widgets(
        request: Request,
        db: Session = Depends(get_db),
        view_builder=Depends(get_view_builder)
):
    """
    Demonstrate the ScheduledQueryResultWidget with different result types.
    """
    # Get some scheduled queries with their latest results
    scheduled_queries = (
        db.query(ScheduledQuery)
        .all()
    )

    widgets = []

    # Add a header
    widgets.append(RawWidget(
        source="<h2>Scheduled Query Result Widgets</h2><p>This page demonstrates the ScheduledQueryResultWidget with different result formats.</p>"
    ))

    # Create widgets for each query's latest result
    for query in scheduled_queries:
        # Create a widget for this query - it will automatically get the latest execution result
        result_widget = ScheduledQueryResultWidget(
            id_scheduled_query=query.id,
            show_query_info=True,
            show_execution_details=True,
            max_table_rows=5,
            render_type=getattr(query, 'render_type', 'auto'),
            title=f"Latest Result: {query.name}",
            db=db,
        )
        #result_widget.process()
        widgets.append(result_widget)

#     # Add information about the test data script
#     widgets.append(RawWidget(
#         source="""
#             <div class="alert alert-info">
#                 <h4><i class="ti ti-info-circle me-2"></i>Test Data Available</h4>
#                 <p>To see more examples with real database data, run the test data creation script:</p>
#                 <pre><code>cd /Users/jerome/Dev/test-fast-pluggy
# python src/fastpluggy_plugin/scheduled_query/examples/create_test_data.py</code></pre>
#                 <p>This will create scheduled queries with various result formats including:</p>
#                 <ul>
#                     <li>Date tuples with datetime objects</li>
#                     <li>Mixed data types (int, bool, string, None)</li>
#                     <li>Single value tuples</li>
#                     <li>JSON arrays and single metrics</li>
#                     <li>Error cases and status messages</li>
#                 </ul>
#                 <p>After running the script, refresh this page to see the widgets populated with real data.</p>
#             </div>
#             """
#     ))

    return view_builder.generate(
        request,
        widgets=widgets,
    )


