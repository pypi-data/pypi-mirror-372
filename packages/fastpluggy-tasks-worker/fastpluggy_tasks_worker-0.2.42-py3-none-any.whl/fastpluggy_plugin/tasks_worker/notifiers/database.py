from datetime import datetime
from typing import Any

from fastpluggy.core.database import Base
from loguru import logger
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from ..notifiers.base import BaseNotifier, NotificationEvent, LogStreamEvent


class NotificationRecordDB(Base):
    __tablename__ = "task_notification_record"
    __table_args__ = {'extend_existing': True}

    task_id = Column(String(200), index=True, nullable=False)
    event_type = Column(String(200), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    content = Column(JSONB)  # Full serialized WebSocketMessage as dict
#    level = Column(String, default="info")  # e.g., 'info', 'warning', 'error'
#    data = Column(Text, nullable=True)
#    data_mime_type = Column(Text, nullable=True)
#    data_source = Column(Text, nullable=True)

    def __repr__(self):
        return f"<NotificationRecord(task_id={self.task_id}, event={self.event_type})>"


class DBNotifier(BaseNotifier):
    name = "db_notifier"

    def __init__(self, session_factory: callable, config: dict = None, events=None):
        super().__init__(config=config, events=events)
        self.session_factory = session_factory

    def notify(self, event: NotificationEvent):
        try:
            with self.session_factory() as db:
                record = NotificationRecordDB(
                    task_id=event.task_id,
                    event_type=event.event_type,
                    timestamp=event.timestamp or datetime.utcnow(),
                    content={
                        "task_id": event.task_id,
                        "name": event.name,
                        "function": event.function,
                        "event_type": event.event_type,
                        "message": event.message,
                        "timestamp": event.timestamp.isoformat(),
                        "success": event.success,
                        "error": event.error,
                    }
                )
                db.add(record)
                db.commit()
        except Exception as e:
            logger.warning(f"[DBNotifier] Failed to save event {event.event_type} for {event.task_id}: {e}")

    def handle_log(self, event: LogStreamEvent):
        try:
            with self.session_factory() as db:
                record = NotificationRecordDB(
                    task_id=event.task_id,
                    event_type=event.event_type,
                    timestamp=event.timestamp or datetime.utcnow(),
                    content={
                        "level": event.record.levelname,
                        "message": event.record.getMessage(),
                    }
                )
                db.add(record)
                db.commit()
        except Exception as e:
            logger.warning(f"[DBNotifier] Failed to save event {event.event_type} for {event.task_id}: {e}")

    def on_context(self, task_id: str, key: str, value: Any):
        try:
            with self.session_factory() as db:
                record = NotificationRecordDB(
                    task_id=task_id,
                    event_type="context",
                    timestamp=datetime.utcnow(),
                    content={
                        "task_id": task_id,
                        "key": key,
                        "value": value,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
                db.add(record)
                db.commit()
        except Exception as e:
            logger.warning(f"[DBNotifier] Failed to save context for {task_id}: {e}")
