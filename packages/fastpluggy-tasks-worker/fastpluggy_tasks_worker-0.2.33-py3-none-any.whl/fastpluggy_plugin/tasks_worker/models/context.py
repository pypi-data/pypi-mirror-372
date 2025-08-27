from sqlalchemy.dialects.postgresql import JSONB

from fastpluggy.core.database import Base
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON


class TaskContextDB(Base):
    __tablename__ = "fp_task_contexts"
    __table_args__ = {'extend_existing': True}

    task_id = Column(String(200), index=True)
    parent_task_id = Column(String(200), nullable=True, index=True)  # To track retries

    task_name = Column(String(200), nullable=False)
    func_name = Column(String(200), nullable=False)
    args = Column(JSON, default="[]")
    kwargs = Column(JSON, default="{}")

    notifier_config = Column(JSON, default="[]")
    notifier_rules = Column(JSON, default="[]")
    notifiers= Column(JSON, nullable=True)

    max_retries = Column(Integer, default=0)
    retry_delay = Column(Integer, default=0)

    task_origin = Column(String(200), default="unk")
    allow_concurrent = Column(Boolean, default=True)

    thread_handler= Column(Text, nullable=True)

    extra_context= Column(JSONB, nullable=True)
