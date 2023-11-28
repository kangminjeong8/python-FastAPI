from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Schedule(BaseModel):
    schedule_id: int
    schedule_name: str
    start_time: str
    cycle_type: int
    everyhour_info: str
    daily_info: str
    weekly_info: str
    monthly_info: str
    option: dict
    reg_date: str

    class Config:
        orm_mode = True

class TaskLog(BaseModel):
    log_id: int
    task_id: int
    log_type: str
    changes: dict
    reg_date: str

    class Config:
        orm_mode = True

class TaskResult(BaseModel):
    result_id: int
    task_id: int
    result_type: int
    error: str
    start_time: str
    end_time: str
    reg_date: str

    class Config:
        orm_mode = True

class Task(BaseModel):
    task_id: int
    task_name: str
    task_type: int
    workflow_name_info: dict
    is_using: int
    next_runtime: str
    created_at: str
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    reg_date: datetime
    task_logs: list[TaskLog]
    task_results: list[TaskResult]

    class Config:
        orm_mode = True

# 페이징 정보를 위한 모델 
class Pagination(BaseModel):
    nowPage: int
    startPage: int
    endPage: int
    total: int
    cntPerPage: int
    lastPage: int

# 작업 목록과 페이징 정보를 포함하는 모델임
class TaskList(BaseModel):
    data: List[Task]
    pagination: Pagination