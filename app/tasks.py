from .database import get_db
from .models import Stock, HistoricalStockData, StockIndex, HistoricalStockIndexData, Commodity, HistoricalCommodityData, ExchangeRate, DollarIndex
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import FinanceDataReader as fdr

def update_exchange_rate(db: Session, base_currency: str, target_currency: str, fred_symbol: str):
    print(f"Updating exchange rate: {base_currency}/{target_currency}")
    last_saved_date = db.query(ExchangeRate).filter_by(base_currency=base_currency, target_currency=target_currency).order_by(ExchangeRate.date.desc()).first()
    start_date = datetime(2010, 1, 1) if not last_saved_date else last_saved_date.date + timedelta(days=1)
    exchange_rate_data = fdr.DataReader(fred_symbol, start=start_date, end=datetime.now())

    for date, data in exchange_rate_data.iterrows():
        db.merge(ExchangeRate(
            base_currency=base_currency,
            target_currency=target_currency,
            date=date.date(),
            close=data[fred_symbol.split(':')[1]]
        ))
    db.commit()
    print(f"{fred_symbol} exchange rate updated")

def dollar_rate(db: Session):
    pairs = [
        ('USD', 'EUR', 'FRED:DEXUSEU'),
        ('USD', 'JPY', 'FRED:DEXJPUS'),
        ('USD', 'GBP', 'FRED:DEXUSUK'),
        ('USD', 'CNY', 'FRED:DEXCHUS')
    ]
    for base_currency, target_currency, fred_symbol in pairs:
        update_exchange_rate(db, base_currency, target_currency, fred_symbol)

def update_dollar_index(db: Session):
    print("Updating Dollar Index data...")
    try:
        # 데이터베이스에서 마지막 저장된 날짜를 가져옵니다.
        last_saved_date = db.query(DollarIndex).order_by(DollarIndex.date.desc()).first()
        start_date = datetime(2010, 1, 1) if not last_saved_date else last_saved_date.date + timedelta(days=1)

        # FDR을 통해 달러 인덱스 데이터를 가져옵니다.
        dollar_index_data = fdr.DataReader('DXY', data_source='FED', start=start_date, end=datetime.now())

        for date, data in dollar_index_data.iterrows():
            db.merge(DollarIndex(
                date=date.date(),
                close=data['Close']
            ))

        db.commit()
        print("Dollar Index data updated")

    except Exception as e:
        print(f"Error updating Dollar Index: {e}")

def ticker_update(db: Session):
    print("Updating ticker data...")
    us_stocks = fdr.StockListing('NASDAQ')
    for _, row in us_stocks.iterrows():
        symbol = row['Symbol']
        name = row['Name']
        industry_code = row.get('IndustryCode')
        industry = row.get('Industry')
        exchange = 'NASDAQ'
        currency = 'USD'
        stock = db.query(Stock).filter_by(symbol=symbol).first()
        if stock:
            stock.name = name
            stock.industry_code = industry_code
            stock.industry = industry
            stock.exchange = exchange
            stock.currency = currency
        else:
            stock = Stock(
                symbol=symbol,
                name=name,
                industry_code=industry_code,
                industry=industry,
                exchange=exchange,
                currency=currency
            )
            db.add(stock)
    db.commit()
    print("US stock ticker and industry info updated")

def stock_data_update(db: Session):
    print("Updating stock data...")
    stocks = db.query(Stock).all()
    for stock in stocks:
        try:
            last_saved_date = db.query(HistoricalStockData).filter_by(stock_id=stock.id).order_by(HistoricalStockData.date.desc()).first()
            start_date = datetime(2010, 1, 1) if not last_saved_date else last_saved_date.date + timedelta(days=1)
            stock_data = fdr.DataReader(stock.symbol, start=start_date, end=datetime.now())
            for date, data in stock_data.iterrows():
                historical_data = db.query(HistoricalStockData).filter_by(stock_id=stock.id, date=date.date()).first()
                if historical_data:
                    historical_data.open = data['Open']
                    historical_data.high = data['High']
                    historical_data.low = data['Low']
                    historical_data.close = data['Close']
                    historical_data.volume = data['Volume']
                else:
                    historical_data = HistoricalStockData(
                        stock_id=stock.id,
                        date=date.date(),
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        volume=data['Volume']
                    )
                    db.add(historical_data)
            db.commit()
            print(f"{stock.symbol} stock data updated")
        except Exception as e:
            print(f"Error saving historical data for {stock.symbol}: {e}")

def stock_index_update(db: Session):
    print("Updating stock index data...")
    indices = [
        {'symbol': '^IXIC', 'name': 'NASDAQ Composite'},
        {'symbol': '^DJI', 'name': 'Dow Jones Industrial Average'},
        {'symbol': '^GSPC', 'name': 'S&P 500'},
        {'symbol': '^RUT', 'name': 'Russell 2000'},
        {'symbol': '^N225', 'name': 'Nikkei 225'},
        {'symbol': '^FTSE', 'name': 'FTSE 100'},
        {'symbol': '^GDAXI', 'name': 'DAX'},
        {'symbol': '^FCHI', 'name': 'CAC 40'},
        {'symbol': '^HSI', 'name': 'Hang Seng Index'},
        {'symbol': '000001.SS', 'name': 'Shanghai Composite'},
        {'symbol': '^KS11', 'name': 'KOSPI'},
        {'symbol': '^AXJO', 'name': 'S&P/ASX 200'},
        {'symbol': '^SP500-45', 'name': 'S&P 500 Information Technology'},
        {'symbol': '^SP500-35', 'name': 'S&P 500 Healthcare'},
        {'symbol': '^SP500-40', 'name': 'S&P 500 Financials'},
        {'symbol': 'AGG', 'name': 'Bloomberg Barclays US Aggregate Bond Index'},
        {'symbol': 'BAGL', 'name': 'Bloomberg Barclays Global Aggregate Bond Index'}
    ]

    for index_info in indices:
        index = db.query(StockIndex).filter_by(symbol=index_info['symbol']).first()
        if not index:
            index = StockIndex(
                symbol=index_info['symbol'],
                name=index_info['name']
            )
            db.add(index)
            db.commit()

        try:
            last_saved_date = db.query(HistoricalStockIndexData).filter_by(index_id=index.id).order_by(HistoricalStockIndexData.date.desc()).first()
            start_date = datetime(2010, 1, 1) if not last_saved_date else last_saved_date.date + timedelta(days=1)
            index_data = fdr.DataReader(index.symbol, start=start_date, end=datetime.now())
            for date, data in index_data.iterrows():
                historical_index_data = db.query(HistoricalStockIndexData).filter_by(index_id=index.id, date=date.date()).first()
                if historical_index_data:
                    historical_index_data.open = data['Open']
                    historical_index_data.high = data['High']
                    historical_index_data.low = data['Low']
                    historical_index_data.close = data['Close']
                    historical_index_data.volume = data.get('Volume', None)
                else:
                    historical_index_data = HistoricalStockIndexData(
                        index_id=index.id,
                        date=date.date(),
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        volume=data.get('Volume', None)
                    )
                    db.add(historical_index_data)
            db.commit()
            print(f"{index.symbol} index data updated")
        except Exception as e:
            print(f"Error saving historical data for {index.symbol}: {e}")

def commodity_data_update(db: Session):
    print("Updating commodity data...")
    commodities = [
        {'symbol': 'GC', 'name': 'Gold'},
        {'symbol': 'SI', 'name': 'Silver'},
        {'symbol': 'CL', 'name': 'Crude Oil'},
        {'symbol': 'NG', 'name': 'Natural Gas'},
        {'symbol': 'HG', 'name': 'Copper'},
        {'symbol': 'PL', 'name': 'Platinum'},
        {'symbol': 'PA', 'name': 'Palladium'}
    ]

    for commodity_info in commodities:
        commodity = db.query(Commodity).filter_by(symbol=commodity_info['symbol']).first()
        if not commodity:
            commodity = Commodity(
                symbol=commodity_info['symbol'],
                name=commodity_info['name']
            )
            db.add(commodity)
            db.commit()

        try:
            last_saved_date = db.query(HistoricalCommodityData).filter_by(commodity_id=commodity.id).order_by(HistoricalCommodityData.date.desc()).first()
            start_date = datetime(2010, 1, 1) if not last_saved_date else last_saved_date.date + timedelta(days=1)
            commodity_data = fdr.DataReader(commodity.symbol, data_source='COMMODITY', start=start_date, end=datetime.now())
            for date, data in commodity_data.iterrows():
                historical_commodity_data = db.query(HistoricalCommodityData).filter_by(commodity_id=commodity.id, date=date.date()).first()
                if historical_commodity_data:
                    historical_commodity_data.open = data['Open']
                    historical_commodity_data.high = data['High']
                    historical_commodity_data.low = data['Low']
                    historical_commodity_data.close = data['Close']
                    historical_commodity_data.volume = data.get('Volume', None)
                else:
                    historical_commodity_data = HistoricalCommodityData(
                        commodity_id=commodity.id,
                        date=date.date(),
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        volume=data.get('Volume', None)
                    )
                    db.add(historical_commodity_data)
            db.commit()
            print(f"{commodity.symbol} commodity data updated")
        except Exception as e:
            print(f"Error saving historical data for {commodity.symbol}: {e}")
