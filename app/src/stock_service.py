# app/src/stock_service.py
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import HistoricalStockData, Stock

def get_stock_data(db: Session, stock_symbol: str, months: int = 3):
    # 데이터 시작 날짜 설정 (예: 3개월 전)
    start_date = datetime.now().date() - timedelta(days=30 * months)

    # Stock 모델을 사용하여 stock_symbol에 해당하는 stock_id 찾기
    stock = db.query(Stock).filter(Stock.symbol == stock_symbol).first()
    if not stock:
        raise ValueError(f"Stock with symbol {stock_symbol} not found.")

    # HistoricalStockData에서 stock_id로 데이터 조회
    historical_data = db.query(HistoricalStockData).filter(
        HistoricalStockData.stock_id == stock.id,
        HistoricalStockData.date >= start_date
    ).order_by(HistoricalStockData.date).all()
    
    return historical_data
