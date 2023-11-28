from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, JSON as Json
from sqlalchemy.orm import relationship

from .database import Base

from datetime import datetime

class Schedule(Base):
    __tablename__ = "schedule"

    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_name = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    cycle_type = Column(Integer, nullable=False)
    everyhour_info = Column(String)
    daily_info = Column(String)
    weekly_info = Column(String)
    monthly_info = Column(String)
    option = Column(Json, nullable=False)
    reg_date = Column(String, nullable=False, default=datetime.now())

class Task(Base):
    __tablename__ = "task"

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=False)
    task_type = Column(Integer, nullable=False)
    workflow_name_info = Column(Json, nullable=False)
    is_using = Column(Integer)
    next_runtime = Column(String)
    created_at = Column(String)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    reg_date = Column(DateTime, default=datetime.now().isoformat())

    task_logs = relationship("TaskLog", back_populates="task")
    task_results = relationship("TaskResult", back_populates="task")

class TaskLog(Base):
    __tablename__ = "task_log"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("task.task_id"), nullable=False)
    log_type = Column(String, nullable=False)
    changes = Column(Json)
    reg_date = Column(String, default=datetime.now())

    task = relationship("Task", back_populates="task_logs")

class TaskResult(Base):
    __tablename__ = "task_result"

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("task.task_id"), nullable=False)
    result_type = Column(Integer, nullable=False)
    error = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    reg_date = Column(String, default=datetime.now())

    task = relationship("Task", back_populates="task_results")
