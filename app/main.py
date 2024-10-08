from fastapi import FastAPI
from .database import engine
from . import models, scheduler
from typing import List, Dict
from .src import allNewsCollection, mainNewsCollection
from .routers import stock_index_endpoints, exchangeRate_live, stock_endpoints, exchange_rate_endpoints, dollar_index_endpoints

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def on_startup():
  scheduler.start_scheduler()

@app.get("/")
def read_root():
  return {"message": "FastAPI is running!"}

# 나스닥 실시간 뉴스 출력
@app.get("/us-stock-news", response_model=List[Dict[str, str]])
def fetch_us_stock_news():
    return allNewsCollection.get_us_stock_news()

app.include_router(exchangeRate_live.router)
app.include_router(stock_endpoints.router)
app.include_router(stock_index_endpoints.router)
app.include_router(exchange_rate_endpoints.router)
app.include_router(dollar_index_endpoints.router)

# 아래 코드로 서버 실행
# uvicorn app.main:app --reload