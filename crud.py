from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text, bindparam
from typing import List, Tuple
from datetime import datetime
from . import models, schemas
import logging

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
    '실패': '0',
    '성공': '1',
    '작업 중': '2',
    '작업 시작 전': '-1'
}

def get_tasks_search(db: Session, page: int = 1, limit: int = 10, key: str = None, content: str = None) -> Tuple[List[models.Task], int, int]:
    # 기본 쿼리
    query = db.query(models.Task)

    joined = query.join(models.TaskResult, models.Task.task_id == models.TaskResult.task_id)

    

    # 검색 조건이 있는 경우 쿼리 수정
    if key and content:
        if key in field_mapping:
            field = field_mapping[key]
            if key == "selTableNmEng":
                result = joined.filter(func.json_extract(field, '$.0.WorkflowName').like(f'%{content}%'))
            elif key == "selModifyDate":
            # 입력된 내용에 따라 날짜 형식을 다르게 생성
                if len(content) == 4:  # 년도만 입력된 경우
                  result = joined.filter(func.strftime('%Y', field) == content)
                elif len(content) == 6:  # 년도와 월이 입력된 경우
                  result = joined.filter(func.strftime('%Y-%m', field) == content[:4] + '-' + content[4:])
                elif len(content) == 8:  # 년도, 월, 일이 모두 입력된 경우
                  result = joined.filter(func.strftime('%Y-%m-%d', field) == content[:4] + '-' + content[4:6] + '-' + content[6:])
                else:
                    return [], 0, 0
            elif key == "selWorkflowState":
                # 입력된 상태 문자열이 매핑된 상태의 일부인지 확인
                status_values = [value for status, value in status_map.items() if content in status]
                if status_values:
                    # 일치하는 모든 result_type 값으로 필터링
                    result = joined.filter(models.TaskResult.result_type.in_(status_values))
                else:
                    # 일치하는 상태가 없는 경우, 결과 없음
                    return [], 0, 0
            else:
                result = joined.filter(field.contains(content))
    # 총 개수 계산 (검색 조건 적용 후)

    fetched = result.order_by(models.Task.task_id.desc()).offset((page - 1) * limit).limit(limit)     

    print(fetched.statement.compile(compile_kwargs={"literal_binds": True}))
    # 페이징 적용
    tasks = fetched.all()
    total_count = fetched.count()
    last_page = (total_count - 1) // limit + 1

    return tasks, total_count, last_page


def get_task_one(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.task_id == task_id).first()
