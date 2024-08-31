from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
from ..src import commodity_service
from ..database import get_db

router = APIRouter()

@router.get("/commodity/{commodity_symbol}/graph")
def get_commodity_graph(commodity_symbol: str, months: int = 3, db: Session = Depends(get_db)):
    try:
        data = commodity_service.get_commodity_data(db, commodity_symbol, months)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not data:
        raise HTTPException(status_code=404, detail="Data not found")

    dates = [record.date for record in data]
    closes = [record.close for record in data]

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(x=dates, y=closes, mode='lines+markers', name='Close'))

    fig.update_layout(
        title=f"Commodity {commodity_symbol} - Last {months} Months",
        xaxis_title="Date",
        yaxis_title="Closing Price",
        hovermode="x"
    )

    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return {"commodity_symbol": commodity_symbol, "graph": graph_json}
