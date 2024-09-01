# app/src/financial_data_service.py

import FinanceDataReader as fdr
from sqlalchemy.orm import Session
from ..models import FinancialData, Stock
from datetime import datetime

def fetch_financial_data(symbol: str):
    """
    특정 주식 심볼에 대한 재무 데이터를 가져옵니다.
    """
    # FinanceDataReader의 get_financial_data 함수 사용
    financials = fdr.DataReader(symbol, data_type='financial')

    # 필요한 데이터만 추출
    data = {
        'revenue': financials.get('Revenue', None),
        'net_income': financials.get('NetIncome', None),
        'total_assets': financials.get('TotalAssets', None),
        'total_liabilities': financials.get('TotalLiabilities', None),
        'equity': financials.get('Equity', None),
        'earnings_per_share': financials.get('EarningsPerShare', None),
        'debt_to_equity_ratio': financials.get('DebtToEquityRatio', None),
    }

    return data

# app/src/financial_data_service.py

def save_financial_data(db: Session, stock_symbol: str, data: dict):
    """
    주식 심볼과 데이터를 받아 데이터베이스에 저장합니다.
    """
    # Stock 테이블에서 stock_id를 찾기
    stock = db.query(Stock).filter(Stock.symbol == stock_symbol).first()
    if not stock:
        raise ValueError(f"Stock with symbol {stock_symbol} not found.")

    # 데이터 저장
    financial_data = FinancialData(
        stock_id=stock.id,
        date=datetime.now().date(),
        revenue=data['revenue'],
        net_income=data['net_income'],
        total_assets=data['total_assets'],
        total_liabilities=data['total_liabilities'],
        equity=data['equity'],
        earnings_per_share=data['earnings_per_share'],
        debt_to_equity_ratio=data['debt_to_equity_ratio'],
    )

    db.add(financial_data)
    db.commit()
    db.refresh(financial_data)

    return financial_data
