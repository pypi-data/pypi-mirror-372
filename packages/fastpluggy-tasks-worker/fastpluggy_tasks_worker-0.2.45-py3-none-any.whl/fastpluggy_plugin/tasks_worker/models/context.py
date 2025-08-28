from sqlalchemy import Column, String, Boolean, Integer, Index
from sqlalchemy.dialects.postgresql import JSONB

from fastpluggy.core.database import Base


class TaskContextDB(Base):
    __tablename__ = "fp_task_contexts"
    __table_args__ = (
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(200), primary_key=True)
    parent_task_id = Column(String(200), nullable=True, index=True)

    task_name = Column(String(200), nullable=False, index=True)
    func_name = Column(String(200), nullable=False)

    args = Column(JSONB, default=list, nullable=False)
    kwargs = Column(JSONB, default=dict, nullable=False)

    notifier_config = Column(JSONB, default=list, nullable=False)
    notifier_rules = Column(JSONB, default=list, nullable=False)
    notifiers = Column(JSONB, nullable=True)

    max_retries = Column(Integer, default=0, nullable=False)
    retry_delay = Column(Integer, default=0, nullable=False)

    task_origin = Column(String(200), default="unk", nullable=False)
    allow_concurrent = Column(Boolean, default=True, nullable=False)
    task_type = Column(String(200), default=None, nullable=True)

    extra_context = Column(JSONB, nullable=True)
