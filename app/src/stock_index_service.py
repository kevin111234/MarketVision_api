from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import HistoricalStockIndexData

def get_stock_data(db: Session, index_id: int, months: int = 3):
    start_date = datetime.now().date() - timedelta(days=30 * months)
    return db.query(HistoricalStockIndexData).filter(
        HistoricalStockIndexData.index_id == index_id,
        HistoricalStockIndexData.date >= start_date
    ).order_by(HistoricalStockIndexData.date).all()
