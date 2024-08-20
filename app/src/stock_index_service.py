from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import HistoricalStockIndexData

def get_last_three_months_data(db: Session, index_id: int):
    three_months_ago = datetime.now().date() - timedelta(days=90)
    return db.query(HistoricalStockIndexData).filter(
        HistoricalStockIndexData.index_id == index_id,
        HistoricalStockIndexData.date >= three_months_ago
    ).order_by(HistoricalStockIndexData.date).all()
