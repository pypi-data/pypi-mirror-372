from loguru import logger
from prometheus_client import Gauge
# Prometheus Metric Update Function
from prometheus_client import REGISTRY

# Prometheus Registry
prometheus_gauges = {}

prometheus_registry = REGISTRY


def update_prometheus_metric(scheduled_query):
    """
    Updates the Prometheus metric for a scheduled query.
    Evaluates result as a Python object if it's a string.
    """
    try:
        config = scheduled_query.grafana_metric_config
        if not config:
            return

        metric_name = config.get("metric_name")
        labels = config.get("labels", {})

        # Evaluate the result if it's a string
        try:
            if isinstance(scheduled_query.last_result, str):
                result = eval(scheduled_query.last_result)  # Evaluate the string to a Python object
        except Exception as e:
            logger.warning(f"Failed to evaluate result for query {scheduled_query.id}: {e}")
            return

        # Extract the value from the result
        try:
            # Assuming the evaluated result is in a format like [{"count": 42}]
            if isinstance(result, list) and len(result) > 0 and "count" in scheduled_query.query.lower():
                value = float(result[0][0])
            else:
                logger.warning(f"Unexpected evaluated structure for result: {result}")
                return
        except (IndexError, ValueError, TypeError) as e:
            logger.warning(f"Error extracting value for metric {metric_name}: {e}")
            return

        # Create or update the Gauge metric
        if metric_name not in prometheus_registry._names_to_collectors:
            prometheus_gauges[metric_name] = Gauge(
                name=metric_name,
                documentation=f"Metric for query {scheduled_query.query}",
                registry=prometheus_registry
            )

            prometheus_gauges[metric_name].set(value)
        logger.info(f"Prometheus metric {metric_name} updated with value: {value}")

    except Exception as e:
        logger.exception(f"Failed to update Prometheus metric for query {scheduled_query.id}: {e}")
