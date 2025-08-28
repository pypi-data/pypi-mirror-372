import copy
import json
from typing import Any, Dict, List, Optional

from fastpluggy.core.widgets import AbstractWidget
from fastpluggy.core.database import session_scope
from ..models import ScheduledQuery, ScheduledQueryResultHistory


class ScheduledQueryResultWidget(AbstractWidget):
    """
    Display the latest scheduled query result as a table.
    Columns come from ScheduledQuery.last_result_key.
    Result is evaluated via JSON, then ast.literal_eval; otherwise treated as a raw string.
    """

    widget_type = "scheduled_query_result"
    template_name = "scheduled_query/widgets/scheduled_query_result.html.j2"
    category = "scheduled_query"
    description = "Display scheduled query results as a table"
    icon = "database"

    def __init__(
        self,
            db,
            id_scheduled_query: int,
        show_query_info: bool = True,
        show_execution_details: bool = True,
        max_table_rows: int = 10,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if not id_scheduled_query:
            raise ValueError("id_scheduled_query is required")

        self.scheduled_query: Optional[ScheduledQuery] = (
            db.query(ScheduledQuery).filter(ScheduledQuery.id == id_scheduled_query).first()
        )
        if not self.scheduled_query:
            raise ValueError(f"ScheduledQuery with id {id_scheduled_query} not found")

        latest = (
            db.query(ScheduledQueryResultHistory)
            .filter(ScheduledQueryResultHistory.scheduled_query_id == self.scheduled_query.id)
            .order_by(ScheduledQueryResultHistory.executed_at.desc())
            .first()
        )
        self.execution_result = copy.deepcopy(latest) if latest else None

        self.show_query_info = show_query_info
        self.show_execution_details = show_execution_details
        self.max_table_rows = max_table_rows

        self.processed_result: Dict[str, Any] = {}
        self.result_type: str = "no_result"
        self.error_message: Optional[str] = None

    # --- processing ----------------------------------------------------------

    def process(self, **kwargs) -> None:
        if not self.execution_result:
            self.result_type = "no_result"
            return

        status = getattr(self.execution_result, "status", "unknown")
        self.error_message = getattr(self.execution_result, "error_message", None)
        raw = getattr(self.execution_result, "result", None)

        if status != "success" or raw is None:
            self.result_type = "error" if self.error_message else "no_result"
            return

        raw_str = str(raw).strip()
        value = self._eval_result(raw_str)

        self.result_type = "table" if value else "no_result"
        self.processed_result = {
            "data": value[: self.max_table_rows],
            "total_rows": len(value),
            "columns": getattr(self.execution_result, "result_key", None),
        }

    def _eval_result(self, s: str) -> Any:
        try:
            return json.loads(s)
        except Exception:
            pass
        try:
            import ast
            return ast.literal_eval(s)
        except Exception:
            pass

        try:
            import datetime
            return eval(s, {"datetime": datetime}, {})
        except Exception:
            pass
        return s  # fallback raw string