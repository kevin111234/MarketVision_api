from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly
import json
from ..database import get_db
from ..models import DollarIndex

router = APIRouter()

@router.get("/dollar-index")
def get_dollar_index_info(db: Session = Depends(get_db)):
    """
    달러 인덱스의 최신 정보를 조회합니다.
    """
    index = db.query(DollarIndex).order_by(DollarIndex.date.desc()).first()
    if not index:
        raise HTTPException(status_code=404, detail="Dollar Index data not found")
    return {"date": index.date, "value": index.value}

@router.get("/dollar-index/historical")
def get_dollar_index_historical(months: int = 3, db: Session = Depends(get_db)):
    """
    달러 인덱스의 최근 n개월 간의 데이터를 조회합니다.
    """
    start_date = datetime.now().date() - timedelta(days=30 * months)
    index_data = db.query(DollarIndex).filter(
        DollarIndex.date >= start_date
    ).order_by(DollarIndex.date).all()

    if not index_data:
        raise HTTPException(status_code=404, detail="No historical data found")

    return [{"date": index.date, "value": index.value} for index in index_data]

@router.get("/dollar-index/graph")
def get_dollar_index_graph(months: int = 3, db: Session = Depends(get_db)):
    """
    달러 인덱스의 변동을 시각화한 그래프를 생성합니다.
    """
    start_date = datetime.now().date() - timedelta(days=30 * months)
    index_data = db.query(DollarIndex).filter(
        DollarIndex.date >= start_date
    ).order_by(DollarIndex.date).all()

    if not index_data:
        raise HTTPException(status_code=404, detail="No historical data found")

    dates = [index.date for index in index_data]
    values = [index.value for index in index_data]

    fig = go.Figure(go.Scatter(x=dates, y=values, mode='lines+markers', name='Dollar Index'))
    fig.update_layout(
        title=f"Dollar Index - Last {months} Months",
        xaxis_title="Date",
        yaxis_title="Index Value",
        hovermode="x"
    )

    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return {"graph": graph_json}
