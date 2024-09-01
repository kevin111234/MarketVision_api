from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly
import json
from ..database import get_db
from ..models import ExchangeRate

router = APIRouter()

@router.get("/exchange-rates/{base}/{target}")
def get_exchange_rate(base: str, target: str, db: Session = Depends(get_db)):
    """
    특정 환율 쌍의 현재 환율 정보를 조회합니다.
    """
    rate = db.query(ExchangeRate).filter(
        ExchangeRate.base_currency == base,
        ExchangeRate.target_currency == target
    ).order_by(ExchangeRate.date.desc()).first()

    if not rate:
        raise HTTPException(status_code=404, detail="Exchange rate data not found")
    
    return {"base": rate.base_currency, "target": rate.target_currency, "date": rate.date, "close": rate.close}

@router.get("/exchange-rates/{base}/{target}/historical")
def get_exchange_rate_historical(base: str, target: str, months: int = 3, db: Session = Depends(get_db)):
    """
    특정 환율 쌍의 최근 n개월 간의 환율 데이터를 조회합니다.
    """
    start_date = datetime.now().date() - timedelta(days=30 * months)
    rates = db.query(ExchangeRate).filter(
        ExchangeRate.base_currency == base,
        ExchangeRate.target_currency == target,
        ExchangeRate.date >= start_date
    ).order_by(ExchangeRate.date).all()

    if not rates:
        raise HTTPException(status_code=404, detail="No historical data found")
    
    return [{"date": rate.date, "close": rate.close} for rate in rates]

@router.get("/exchange-rates/{base}/{target}/graph")
def get_exchange_rate_graph(base: str, target: str, months: int = 3, db: Session = Depends(get_db)):
    """
    특정 환율 쌍의 환율 변동을 시각화한 그래프를 생성합니다.
    """
    start_date = datetime.now().date() - timedelta(days=30 * months)
    rates = db.query(ExchangeRate).filter(
        ExchangeRate.base_currency == base,
        ExchangeRate.target_currency == target,
        ExchangeRate.date >= start_date
    ).order_by(ExchangeRate.date).all()

    if not rates:
        raise HTTPException(status_code=404, detail="No historical data found")

    dates = [rate.date for rate in rates]
    closes = [rate.close for rate in rates]

    fig = go.Figure(go.Scatter(x=dates, y=closes, mode='lines+markers', name='Close'))
    fig.update_layout(
        title=f"Exchange Rate {base}/{target} - Last {months} Months",
        xaxis_title="Date",
        yaxis_title="Rate",
        hovermode="x"
    )

    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return {"base": base, "target": target, "graph": graph_json}
