from fastapi import FastAPI
from .database import engine
from . import models, scheduler

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def on_startup():
  scheduler.start_scheduler()

@app.get("/")
def read_root():
  return {"message": "FastAPI is running!"}

# 아래 코드로 서버 실행
# uvicorn app.main:app --reload