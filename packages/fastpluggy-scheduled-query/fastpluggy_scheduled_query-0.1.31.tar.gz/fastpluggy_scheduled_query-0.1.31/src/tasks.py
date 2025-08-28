import asyncio
import datetime
import time
from typing import Annotated

from fastpluggy.core.database import session_scope
from fastpluggy.core.tools.inspect_tools import InjectDependency
from fastpluggy.fastpluggy import FastPluggy
from loguru import logger
from sqlalchemy import text

from fastpluggy_plugin.tasks_worker.task_registry import task_registry
from .config import ScheduledQuerySettings
from .metrics import update_prometheus_metric
from .models import ScheduledQuery
from .models import ScheduledQueryResultHistory


def is_query_safe(query: str) -> bool:
    settings = ScheduledQuerySettings()
    dict_forbidden_keywords = {kw.strip() for kw in settings.forbidden_keywords.split(',')}
    return not any(keyword in query.lower() for keyword in dict_forbidden_keywords)


async def execute_scheduled_query(scheduled_query_id):

    with session_scope() as db:
        settings = ScheduledQuerySettings()

        try:
            scheduled_query = db.query(ScheduledQuery).filter(ScheduledQuery.id == scheduled_query_id).first()
            if not scheduled_query:
                logger.warning(f"Query with ID {scheduled_query_id} not found.")
                return

            if not is_query_safe(scheduled_query.query):
                scheduled_query.last_result = "Query rejected: contains forbidden keywords."
                scheduled_query.last_executed = datetime.datetime.now(tz=datetime.timezone.utc)
                db.commit()
                return

            start_time = time.perf_counter()
            result = db.execute(text(scheduled_query.query))
            db.commit()

            duration_ms = int((time.perf_counter() - start_time) * 1000)

            if scheduled_query.query.strip().lower().startswith("select"):
                result_str = str(result.fetchall())
            else:
                result_str = f"Rows affected: {result.rowcount}"

            # Update last execution
            scheduled_query.last_result = result_str
            # Handle case where result.keys() might be None or not callable
            keys = []
            try:
                keys_result = result.keys()
                if keys_result is not None:
                    keys = list(keys_result)
            except (TypeError, AttributeError):
                logger.warning(f"Could not get keys from result for query {scheduled_query_id}")

            scheduled_query.last_result_key = keys
            scheduled_query.last_executed = datetime.datetime.now(tz=datetime.timezone.utc)
            db.add(scheduled_query)
            db.commit()

            # Store execution history
            if settings.enable_history:
                history = ScheduledQueryResultHistory(
                    scheduled_query_id=scheduled_query.id,
                    executed_at=scheduled_query.last_executed,
                    duration_ms=duration_ms,
                    result=result_str,
                    # Using the safely extracted keys from above
                    result_key=keys,
                    status="success"
                )
                db.add(history)
                db.commit()
            db.refresh(scheduled_query)

            logger.info(f"Query {scheduled_query.id} executed successfully with result: {result_str}")

        except Exception as e:
            logger.exception(f"Error executing query {scheduled_query_id}: {e}")
            db.rollback()

            error_msg = str(e)
            now = datetime.datetime.now(tz=datetime.timezone.utc)

            # Update last result
            if scheduled_query:
                scheduled_query.last_result = f"Error: {error_msg}"
                scheduled_query.last_executed = now

            # Store failed execution history
            history = ScheduledQueryResultHistory(
                scheduled_query_id=scheduled_query_id,
                executed_at=now,
                duration_ms=None,
                result=None,
                status="failed",
                error_message=error_msg,
            )
            db.add(history)
            db.commit()




@task_registry.register(name="schedule_loop", allow_concurrent=False, task_type="fp-daemon")
def collect_execute_scheduled_query(fast_pluggy: Annotated[FastPluggy, InjectDependency], ):
    from .config import ScheduledQuerySettings
    runner = fast_pluggy.get_global('tasks_worker')

    while runner.executor.is_running():
        with session_scope() as db:
            try:
                list_query = db.query(ScheduledQuery).filter(ScheduledQuery.enabled == True).all()
                for item in list_query:

                    settings = ScheduledQuerySettings()
                    if settings.notification_on_run:
                        # todo: refactor this to use notifer
                        pass
                        # ws_manager.sync_broadcast(
                        #    message=WebSocketMessagePayload(message=f'Run scheduled query {item.query}')
                        # ) if ws_manager else None
                    logger.debug(f"Collecting execute scheduled query : {item}")
                    asyncio.run(execute_scheduled_query(item.id))

                    # Update Prometheus metrics
                    if settings.prometheus_enabled and item.grafana_metric_config:
                        update_prometheus_metric(item)

                    time.sleep(settings.interval)
            except Exception as e:
                logger.exception(f"Error in scheduled query execution: {e}")
