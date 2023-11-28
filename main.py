from fastapi import Depends, FastAPI, HTTPException, Request, Response, Query
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas, database
from .database import SessionLocal, engine
from .schemas import TaskList, Task

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/schedules/", response_model=list[schemas.Schedule])
async def get_schedules(db: Session = Depends(get_db)):
    schedules = crud.get_schedules(db)
    return schedules

@app.get("/schedules/{schedule_id}", response_model=schemas.Schedule)
async def get_schedule_one(schedule_id: int, db: Session = Depends(get_db)):
    db_schedule = crud.get_schedule_one(db, schedule_id=schedule_id)
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

@app.get("/tasks/", response_model=list[Task])
async def get_tasks(db: Session = Depends(database.get_db)):
    tasks = crud.get_tasks(db)

    return tasks

# @app.get("/tasks/search", response_model=TaskList)
# async def get_tasks_search(db: Session = Depends(database.get_db), page: int = Query(1, alias="page"), limit: int = Query(10, alias="limit")):
#     tasks, total_count, last_page = crud.get_tasks_search(db, page=page, limit=limit)
#     total_pages = (total_count + limit - 1) // limit

#     return {
#         "data": tasks,
#         "pagination": {
#             "nowPage": page,
#             "startPage": max(1, page - 5),
#             "endPage": min(last_page, page + 5),
#             "total": total_count,
#             "cntPerPage": limit,
#             "lastPage": last_page
#         }
#     }

@app.get("/tasks/search", response_model=TaskList)
async def get_tasks_search(
    db: Session = Depends(database.get_db), 
    page: int = Query(1, alias="page"), 
    limit: int = Query(10, alias="limit"),
    key: Optional[str] = None,  # 검색 키 추가 (옵셔널)
    content: Optional[str] = None  # 검색 내용 추가 (옵셔널)
):
    tasks, total_count, last_page = crud.get_tasks_search(db, page=page, limit=limit, key=key, content=content)
    total_pages = (total_count + limit - 1) // limit

    return {
        "pagination": {
            "nowPage": page,
            "startPage": max(1, page - 5),
            "endPage": min(last_page, page + 5),
            "total": total_count,
            "cntPerPage": limit,
            "lastPage": last_page
        },
        "data": tasks
    }

@app.get("/tasks/{task_id}", response_model=schemas.Task)
async def get_task_one(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task_one(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task