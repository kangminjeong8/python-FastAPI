from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Tuple
from . import models

def get_schedules(db: Session):
    return db.query(models.Schedule).all()

def get_schedule_one(db: Session, schedule_id: int):
    return db.query(models.Schedule).filter(models.Schedule.schedule_id == schedule_id).first()

def get_tasks(db: Session):
    return db.query(models.Task).all()

field_mapping = {
    "selTableNmEng": models.Task.workflow_name_info,
    "selTableNmKor": models.Task.task_name,
    "selModifyDate": models.TaskResult.end_time,
    "selWorkflowState": models.TaskResult.result_type
}

status_map = {
    '실패': 0,
    '성공': 1,
    '작업 중': 2,
    '작업 시작 전': -1
}

def get_tasks_search(
        db: Session, 
        page: int = 1, 
        limit: int = 10,
        key: str = None, 
        content: str = None,
        startdate: str = None,
        enddate: str = None) -> Tuple[List[models.Task], int, int]:
    
    # 기본 쿼리
    query = db.query(models.Task)

    subquery = (
        db.query(
            models.TaskResult.task_id,
            models.TaskResult.result_type,
            func.max(models.TaskResult.end_time).label('max_end_time')
        )
        .group_by(models.TaskResult.task_id)
        .subquery()
    )
    query = db.query(models.Task).join(subquery, models.Task.task_id == subquery.c.task_id)
    joined = query.join(models.Schedule, models.Task.schedule_id == models.Schedule.schedule_id)

        # 검색 조건
    if key == 'all':
        result = joined
    elif key in field_mapping:
        field = field_mapping[key]
        if key == "selTableNmEng":
            result = joined.filter(func.json_extract(field, '$.0.WorkflowName').like(f'%{content}%'))
        elif key == "selModifyDate":
            # selModifyDate의 경우 content 대신 startdate와 enddate 사용
            start_date_str = f"{startdate} 00:00:00"
            end_date_str = f"{enddate} 23:59:59"
            result = joined.filter(subquery.c.max_end_time.between(start_date_str, end_date_str))
        elif key == "selWorkflowState":
            # status_map을 사용하여 상태 코드에 따른 검색 수행
            status_values = [value for status, value in status_map.items() if content in status]
            if status_values:
                result = joined.filter(subquery.c.result_type.in_(status_values))
            else:
                return [], 0, 0
        else:
            result = joined.filter(field.contains(content))
    else:
        result = joined    

    result = result.filter(models.Task.deleted_at.is_(None))
    
    fetched = result.offset((page - 1) * limit).limit(limit)     
    tasks = fetched.all()
    total_count = result.count()
    last_page = (total_count - 1) // limit + 1  

    print(fetched.statement.compile(compile_kwargs={"literal_binds": True}))

    return tasks, total_count, last_page

def get_task_one(
    db: Session,
    task_id: int,
    page: int = 1,
    limit: int = 10,
    key: str = None,
    startdate: str = None,
    enddate: str = None
) -> Tuple[List[models.TaskResult], int, int]:
    
    # 상태 매핑
    status_map = {
        'fail': 0,
        'success': 1,
        'inProgress': 2,
        'notStart': -1
    }
    
    # 기본 쿼리: task_id에 해당하는 Task 객체 검색
    query = db.query(models.TaskResult).filter(models.TaskResult.task_id == task_id)
    
    # 선택적 검색 조건 적용
    if key in status_map:
        query = query.filter(models.TaskResult.result_type == status_map[key])

    if startdate and enddate:
        start_date_str = f"{startdate} 00:00:00"
        end_date_str = f"{enddate} 23:59:59"
        query = query.filter(models.TaskResult.end_time.between(start_date_str, end_date_str))    

    # 페이지네이션 적용
    task_results = query.order_by(models.TaskResult.task_id).offset((page - 1) * limit).limit(limit).all()
    total_count = query.count()
    last_page = (total_count - 1) // limit + 1 if total_count > 0 else 1

    print(startdate, enddate)
    print(query.statement.compile(compile_kwargs={"literal_binds": True}))

    return task_results, total_count, last_page
