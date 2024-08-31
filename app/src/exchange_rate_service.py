from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import ExchangeRate

def get_exchange_rate_data(db: Session, base_currency: str, target_currency: str, months: int = 3):
    # 데이터 시작 날짜 설정 (예: 3개월 전)
    start_date = datetime.now().date() - timedelta(days=30 * months)

    # ExchangeRate에서 base_currency와 target_currency로 데이터 조회
    exchange_rate_data = db.query(ExchangeRate).filter(
        ExchangeRate.base_currency == base_currency,
        ExchangeRate.target_currency == target_currency,
        ExchangeRate.date >= start_date
    ).order_by(ExchangeRate.date).all()
    
    return exchange_rate_data
