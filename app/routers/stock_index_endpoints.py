from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly
import json
from ..database import get_db
from ..models import HistoricalStockIndexData, StockIndex

router = APIRouter()

@router.get("/stock-index/{index_id}/info")
def get_stock_index_info(index_id: int, db: Session = Depends(get_db)):
    """
    특정 주식 인덱스의 기본 정보를 조회합니다.
    """
    index = db.query(StockIndex).filter(StockIndex.id == index_id).first()
    if not index:
        raise HTTPException(status_code=404, detail="Stock Index not found")
    return {"index_id": index.id, "symbol": index.symbol, "name": index.name}

@router.get("/stock-index/{index_id}/historical")
def get_stock_index_historical(index_id: int, months: int = 3, db: Session = Depends(get_db)):
    """
    특정 주식 인덱스의 최근 n개월 간의 가격 데이터를 조회합니다.
    """
    start_date = datetime.now().date() - timedelta(days=30 * months)
    index_data = db.query(HistoricalStockIndexData).filter(
        HistoricalStockIndexData.index_id == index_id,
        HistoricalStockIndexData.date >= start_date
    ).order_by(HistoricalStockIndexData.date).all()

    if not index_data:
        raise HTTPException(status_code=404, detail="No historical data found")
    
    # Convert data to dictionary list for JSON response
    return [{"date": record.date, "open": record.open, "high": record.high,
              "low": record.low, "close": record.close, "volume": record.volume}
            for record in index_data]

@router.get("/stock-index/{index_id}/graph")
def get_stock_index_graph(index_id: int, months: int = 3, db: Session = Depends(get_db)):
    """
    특정 주식 인덱스의 가격 변동을 시각화한 그래프를 생성합니다.
    """
    start_date = datetime.now().date() - timedelta(days=30 * months)
    index_data = db.query(HistoricalStockIndexData).filter(
        HistoricalStockIndexData.index_id == index_id,
        HistoricalStockIndexData.date >= start_date
    ).order_by(HistoricalStockIndexData.date).all()

    if not index_data:
        raise HTTPException(status_code=404, detail="No historical data found")

    dates = [record.date for record in index_data]
    closes = [record.close for record in index_data]

    fig = go.Figure(go.Scatter(x=dates, y=closes, mode='lines+markers', name='Close'))
    fig.update_layout(
        title=f"Stock Index {index_id} - Last {months} Months",
        xaxis_title="Date",
        yaxis_title="Closing Price",
        hovermode="x"
    )

    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return {"index_id": index_id, "graph": graph_json}