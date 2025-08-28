from sqlalchemy import DateTime, Text, Boolean, JSON, Index
from sqlalchemy.orm import mapped_column
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from fastpluggy.core.database import Base


class ScheduledQuery(Base):
    __tablename__ = 'fp_scheduled_queries'
    __table_args__ = {'extend_existing': True}

    name = mapped_column(Text, nullable=False)
    query = mapped_column(Text, nullable=False)
    cron_schedule = mapped_column(Text, nullable=False)  # CRON syntax
    last_executed = mapped_column(DateTime, default=None)

    grafana_metric_config = mapped_column(
        JSON, nullable=True, default=None
    )  # Grafana metric export configuration

    enabled = mapped_column(Boolean, nullable=False, default=False)

    last_result = mapped_column(Text, nullable=True)  # Last query result
    last_result_key = mapped_column(JSON, nullable=True)  # Last query result key
    
    render_type = mapped_column(Text, nullable=True, default="auto")  # How to render results: auto, table, counter, metric, raw

    def __repr__(self) -> str:
        return (
            f"ScheduledQuery(id={self.id}, name={self.name},query={self.query}, "
            f"cron_schedule={self.cron_schedule}, last_executed={self.last_executed}, "
            f"last_result={self.last_result}, enabled={self.enabled}, "
            f"grafana_metric_config={self.grafana_metric_config})"
        )


class ScheduledQueryResultHistory(Base):
    __tablename__ = 'fp_scheduled_query_results'
    __table_args__ = (
        Index('ix_query_history_recent', 'scheduled_query_id', 'executed_at'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    scheduled_query_id = Column(ForeignKey('fp_scheduled_queries.id'), nullable=False, index=True)

    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_ms = Column(Integer, nullable=True)  # Execution time in milliseconds
    result = Column(Text, nullable=True)  # Truncated or full query result
    result_key = Column(JSON, nullable=True)  # Truncated or full query result
    status = Column(Text, nullable=False, default="success")  # 'success', 'failed', 'timeout', etc.
    error_message = Column(Text, nullable=True)  # Full error traceback or message

    grafana_metrics_snapshot = Column(JSON, nullable=True)  # Optional snapshot of metrics

    query = relationship("ScheduledQuery", backref="execution_history")

    def __repr__(self):
        return (
            f"<ScheduledQueryResultHistory(id={self.id}, query_id={self.scheduled_query_id}, "
            f"executed_at={self.executed_at}, duration_ms={self.duration_ms}, "
            f"status={self.status})>"
        )
