from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
from ..src import exchange_rate_service
from ..database import get_db

router = APIRouter()

@router.get("/exchange-rate/{base_currency}/{target_currency}/graph")
def get_exchange_rate_graph(base_currency: str, target_currency: str, months: int = 3, db: Session = Depends(get_db)):
    try:
        data = exchange_rate_service.get_exchange_rate_data(db, base_currency, target_currency, months)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not data:
        raise HTTPException(status_code=404, detail="Data not found")

    dates = [record.date for record in data]
    closes = [record.close for record in data]

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(x=dates, y=closes, mode='lines+markers', name='Exchange Rate'))

    fig.update_layout(
        title=f"Exchange Rate {base_currency}/{target_currency} - Last {months} Months",
        xaxis_title="Date",
        yaxis_title="Exchange Rate",
        hovermode="x"
    )

    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return {"base_currency": base_currency, "target_currency": target_currency, "graph": graph_json}
