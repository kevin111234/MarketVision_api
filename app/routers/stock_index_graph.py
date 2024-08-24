from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
from ..src.stock_index_service import get_stock_data
from ..database import get_db

router = APIRouter()

@router.get("/stock-index/{index_id}/data")
def get_stock_index_data(index_id: int, months: int = 3, db: Session = Depends(get_db)):
    data = get_stock_data(db, index_id, months)

    if not data:
        raise HTTPException(status_code=404, detail="Data not found")

    dates = [record.date for record in data]
    closes = [record.close for record in data]

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(x=dates, y=closes, mode='lines+markers', name='Close'))

    fig.update_layout(
        title=f"Stock Index {index_id} - Last {months} Months",
        xaxis_title="Date",
        yaxis_title="Closing Price",
        hovermode="x"
    )

    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return {"index_id": index_id, "graph": graph_json}
