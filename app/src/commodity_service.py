from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import HistoricalCommodityData, Commodity

def get_commodity_data(db: Session, commodity_symbol: str, months: int = 3):
    # 데이터 시작 날짜 설정 (예: 3개월 전)
    start_date = datetime.now().date() - timedelta(days=30 * months)

    # Commodity 모델을 사용하여 commodity_symbol에 해당하는 commodity_id 찾기
    commodity = db.query(Commodity).filter(Commodity.symbol == commodity_symbol).first()
    if not commodity:
        raise ValueError(f"Commodity with symbol {commodity_symbol} not found.")

    # HistoricalCommodityData에서 commodity_id로 데이터 조회
    historical_data = db.query(HistoricalCommodityData).filter(
        HistoricalCommodityData.commodity_id == commodity.id,
        HistoricalCommodityData.date >= start_date
    ).order_by(HistoricalCommodityData.date).all()
    
    return historical_data
