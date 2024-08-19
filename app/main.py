from fastapi import FastAPI
from .database import engine
from . import models, scheduler
from typing import List, Dict
from .src import allNewsCollection, mainNewsCollection, mainNewsKeyword

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def on_startup():
  scheduler.start_scheduler()

@app.get("/")
def read_root():
  return {"message": "FastAPI is running!"}

# 
@app.get("/us-stock-news", response_model=List[Dict[str, str]])
def fetch_us_stock_news():
    return allNewsCollection.get_us_stock_news()

# 아래 코드로 서버 실행
# uvicorn app.main:app --reload