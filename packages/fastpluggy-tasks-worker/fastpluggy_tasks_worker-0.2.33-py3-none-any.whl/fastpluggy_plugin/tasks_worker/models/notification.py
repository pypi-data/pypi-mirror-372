# from datetime import datetime
#
# from fastpluggy.core.database import Base
# from sqlalchemy import Column, String, DateTime, Integer, Text
#
#
# # TODO : remove this when dbNotifier works
# class TaskNotificationDB(Base):
#     __tablename__ = 'task_notifications'
#     __table_args__ = {'extend_existing': True}
#
#     id = Column(Integer, primary_key=True)
#     task_id = Column(String(200), index=True)
#     event_type = Column(String(200))  # task_started, task_success, task_failed, etc.
#     message = Column(Text)
#     timestamp = Column(DateTime, default=datetime.utcnow)
