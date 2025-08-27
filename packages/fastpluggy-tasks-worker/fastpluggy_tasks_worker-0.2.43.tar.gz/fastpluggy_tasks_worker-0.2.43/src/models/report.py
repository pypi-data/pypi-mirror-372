from fastpluggy.core.database import Base
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Float,JSON


class TaskReportDB(Base):
    __tablename__ = "fp_task_reports"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    task_id = Column(String(200), index=True, unique=True, nullable=False)

    function = Column(String(200), nullable=False)
    args = Column(JSON, default="[]")
    kwargs = Column(JSON, default="{}")

    status = Column(String(200), default="created")  # created ,queued, running, success, failed

    result = Column(Text)
    logs = Column(Text)
    error = Column(JSON)
    tracebacks = Column(JSON)  # rename to tracebacks
    duration = Column(Float)
    attempts = Column(Integer)
    success = Column(Boolean) # maybe can be deleted
    worker_id= Column(Text)

    finished = Column(Boolean, default=False)
    finished_at = Column(DateTime) # maybe same as end_time

    start_time = Column(DateTime)
    end_time = Column(DateTime)
    heartbeat = Column(DateTime)

    thread_native_id= Column(Text)
    thread_ident= Column(Text)