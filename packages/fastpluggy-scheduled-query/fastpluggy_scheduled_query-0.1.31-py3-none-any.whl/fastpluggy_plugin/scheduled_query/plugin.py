# plugin.py

from typing import Annotated, Any

from fastpluggy.core.database import create_table_if_not_exist
from loguru import logger

from fastpluggy.core.module_base import FastPluggyBaseModule
from fastpluggy.core.tools.inspect_tools import InjectDependency
from fastpluggy.fastpluggy import FastPluggy

from .config import ScheduledQuerySettings


def get_scheduler_query_router():
    from .routers.web_router import web_router
    from .routers.api_router import api_router
    from .routers.crud_router import crud_router
    return [web_router, api_router, crud_router]

class ScheduledQueryPlugin(FastPluggyBaseModule):

    module_name: str = "scheduled_query"

    module_menu_name: str = "Scheduled Query"
    module_menu_icon: str = "fas fa-edit"

    module_settings: Any = ScheduledQuerySettings
    module_router: Any = get_scheduler_query_router

    depends_on: dict = {
        "tasks_worker": ">=0.2.0",
        "ui_tools": ">=0.0.4",
    }

    def on_load_complete(self, fast_pluggy: Annotated["FastPluggy", InjectDependency]) -> None:
        logger.info("Add query runner to executor")
        settings = ScheduledQuerySettings()
        from .models import ScheduledQuery,ScheduledQueryResultHistory
        create_table_if_not_exist(ScheduledQuery)

        if settings.enable_history:
            create_table_if_not_exist(ScheduledQueryResultHistory)

        from .tasks import collect_execute_scheduled_query

        task_runner = FastPluggy.get_global("tasks_worker")
        if task_runner is None:
            logger.error("Tasks worker not found")
            return
        task_runner.submit(
            collect_execute_scheduled_query,
            task_name='scheduled query',
            notify_config=[],
            task_origin="module_load",
            allow_concurrent=False
        )
