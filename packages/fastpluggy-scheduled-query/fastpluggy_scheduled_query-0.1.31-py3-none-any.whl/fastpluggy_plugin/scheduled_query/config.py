from fastpluggy.core.config import BaseDatabaseSettings


class ScheduledQuerySettings(BaseDatabaseSettings):

    notification_on_run: bool = False

    forbidden_keywords: str= "drop,delete,truncate,alter" # forbidden keywords
    interval: int = 30 # minimal interval

    # history of results
    enable_history: bool = True
    limit_history:int = -1 # max of results to keep -1 is unlimited

    # expose in prometheus metrics
    prometheus_enabled: bool = True
