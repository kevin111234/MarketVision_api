from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import plotly.graph_objs as go
from ..database import get_db
from ..models import Stock, HistoricalStockData
import plotly
import json

router = APIRouter()

@router.get("/stocks/{symbol}/info")
def get_stock_info(symbol: str, db: Session = Depends(get_db)):
    """
    특정 주식의 기본 정보를 조회합니다.
    """
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"symbol": stock.symbol, "name": stock.name}

@router.get("/stocks/{symbol}/historical")
def get_stock_historical(symbol: str, months: int = 3, db: Session = Depends(get_db)):
    """
    특정 주식의 최근 n개월 간의 가격 데이터를 조회합니다.
    """
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # Calculate the start date based on the months parameter
    start_date = datetime.now() - timedelta(days=30 * months)
    stock_data = db.query(HistoricalStockData).filter(
        HistoricalStockData.stock_id == stock.id,
        HistoricalStockData.date >= start_date
    ).all()
    
    if not stock_data:
        raise HTTPException(status_code=404, detail="No historical data found")
    
    # Convert data to dictionary list for JSON response
    return [{"date": data.date, "open": data.open, "high": data.high,
              "low": data.low, "close": data.close, "volume": data.volume}
            for data in stock_data]

@router.get("/stocks/{symbol}/graph")
def get_stock_graph(symbol: str, months: int = 3, db: Session = Depends(get_db)):
    """
    특정 주식의 가격 변동을 시각화한 그래프를 생성합니다.
    """
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    start_date = datetime.now() - timedelta(days=30 * months)
    stock_data = db.query(HistoricalStockData).filter(
        HistoricalStockData.stock_id == stock.id,
        HistoricalStockData.date >= start_date
    ).all()
    
    if not stock_data:
        raise HTTPException(status_code=404, detail="No historical data found")
    
    dates = [data.date for data in stock_data]
    closes = [data.close for data in stock_data]

    fig = go.Figure(go.Scatter(x=dates, y=closes, mode='lines', name='Close Price'))
    fig.update_layout(title=f"{stock.name} Price Over Last {months} Months",
        xaxis_title="Date",
        yaxis_title="Close Price",
        hovermode="x"
    )
    
    # JSON으로 변환할 때 Plotly 인코더 사용
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return {"symbol": symbol, "graph": graph_json}