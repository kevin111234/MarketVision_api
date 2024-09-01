from .database import get_db
from .models import Stock, HistoricalStockData, StockIndex, HistoricalStockIndexData, Commodity, HistoricalCommodityData, ExchangeRate, DollarIndex, EconomicIndicator
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import FinanceDataReader as fdr
import requests
from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy.sql import text
import pandas_datareader as pdr

def update_exchange_rate(db: Session, base_currency: str, target_currency: str, fred_symbol: str):
    print(f"Updating exchange rate: {base_currency}/{target_currency}")
    try:
        last_saved_date = db.query(ExchangeRate).filter_by(base_currency=base_currency, target_currency=target_currency).order_by(ExchangeRate.date.desc()).first()
        start_date = datetime(2010, 1, 1) if not last_saved_date else last_saved_date.date + timedelta(days=1)
        exchange_rate_data = fdr.DataReader(fred_symbol, start=start_date, end=datetime.now())

        # 배치 커밋을 위해 리스트를 사용
        batch_size = 100
        batch = []
        for date, data in exchange_rate_data.iterrows():
            try:
                # UPDATE 옵션을 활용하여 중복 데이터 처리
                db.execute(
                  text(
                    """
                    INSERT INTO ExchangeRate (base_currency, target_currency, date, close)
                    VALUES (:base_currency, :target_currency, :date, :close)
                    ON DUPLICATE KEY UPDATE close = :close
                    """),
                    {
                        'base_currency': base_currency,
                        'target_currency': target_currency,
                        'date': date.date(),
                        'close': data[fred_symbol.split(':')[1]]
                    }
                )
                batch.append(data)
                # 배치 사이즈에 도달하면 커밋
                if len(batch) >= batch_size:
                    db.commit()
                    print(f"Batch committed for {base_currency}/{target_currency}")
                    batch = []
            except Exception as e:
                print(f"Error processing {date.date()} for {base_currency}/{target_currency}: {e}")

        # 남은 데이터 커밋
        if batch:
            db.commit()
            print(f"Final batch committed for {base_currency}/{target_currency}")

    except Exception as e:
        db.rollback()
        print(f"Error updating exchange rate {base_currency}/{target_currency}: {e}")
    finally:
        db.close()

def dollar_rate():
    db = next(get_db())
    try:
        pairs = [
            ('USD', 'EUR', 'FRED:DEXUSEU'),
            ('USD', 'JPY', 'FRED:DEXJPUS'),
            ('USD', 'GBP', 'FRED:DEXUSUK'),
            ('USD', 'CNY', 'FRED:DEXCHUS')
        ]
        for base_currency, target_currency, fred_symbol in pairs:
            update_exchange_rate(db, base_currency, target_currency, fred_symbol)
    finally:
        db.close()

def update_dollar_index():
    db = next(get_db())
    print("Updating Dollar Index data...")
    try:
        last_saved_date = db.query(DollarIndex).order_by(DollarIndex.date.desc()).first()
        start_date = datetime(2010, 1, 1) if not last_saved_date else last_saved_date.date + timedelta(days=1)
        dollar_index_data = fdr.DataReader('FED:DXY', start=start_date, end=datetime.now())

        batch_size = 100
        batch = []
        for date, data in dollar_index_data.iterrows():
            try:
                close_value = data['Close']
                if not pd.isna(close_value):
                    db.merge(DollarIndex(
                        date=date.date(),
                        close=close_value
                    ))
                    batch.append(data)
                    if len(batch) >= batch_size:
                        db.commit()
                        print("Batch committed for Dollar Index")
                        batch = []
            except Exception as e:
                print(f"Error processing {date.date()} for Dollar Index: {e}")

        if batch:
            db.commit()
            print("Final batch committed for Dollar Index")

    except Exception as e:
        db.rollback()
        print(f"Error updating Dollar Index: {e}")
    finally:
        db.close()

def ticker_update():
    db = next(get_db())
    print("Updating ticker data...")
    try:
        us_stocks = fdr.StockListing('NASDAQ')
        batch_size = 100
        batch = []
        for _, row in us_stocks.iterrows():
            try:
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
                batch.append(stock)
                if len(batch) >= batch_size:
                    db.commit()
                    print("Batch committed for ticker update")
                    batch = []
            except Exception as e:
                print(f"Error processing ticker {row['Symbol']}: {e}")

        if batch:
            db.commit()
            print("Final batch committed for ticker update")

    except Exception as e:
        db.rollback()
        print(f"Error updating ticker data: {e}")
    finally:
        db.close()

def stock_data_update():
    db = next(get_db())
    print("Updating stock data...")
    try:
        stocks = db.query(Stock).all()
        batch_size = 100
        batch = []
        for stock in stocks:
            try:
                last_saved_date = db.query(HistoricalStockData).filter_by(stock_id=stock.id).order_by(HistoricalStockData.date.desc()).first()
                start_date = datetime(2010, 1, 1) if not last_saved_date else last_saved_date.date + timedelta(days=1)
                stock_data = fdr.DataReader(stock.symbol, start=start_date, end=datetime.now())

                # NaN 값을 포함한 행을 찾아 출력
                nan_rows = stock_data[stock_data.isna().any(axis=1)]
                if not nan_rows.empty:
                    print("NaN 값을 포함한 행이 발견되었습니다:")
                    print(nan_rows)
                    print("이 부분이 NaN으로 표시되었습니다.")
                
                # NaN 값을 포함한 행 제거
                stock_data = stock_data.dropna()

                for date, data in stock_data.iterrows():
                    try:
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
                        batch.append(historical_data)
                        if len(batch) >= batch_size:
                            db.commit()
                            print(f"Batch committed for {stock.symbol} stock data")
                            batch = []
                    except Exception as e:
                        print(f"Error processing {date.date()} for {stock.symbol}: {e}")
            except Exception as e:
                print(f"Error saving historical data for {stock.symbol}: {e}")

        if batch:
            db.commit()
            print("Final batch committed for stock data")

    except Exception as e:
        print(f"Failed to update stock data: {e}")
    finally:
        db.close()

def stock_index_update():
    db = next(get_db())
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

    try:
        batch_size = 100
        batch = []
        for index_info in indices:
            try:
                index = db.query(StockIndex).filter_by(symbol=index_info['symbol']).first()
                if not index:
                    index = StockIndex(
                        symbol=index_info['symbol'],
                        name=index_info['name']
                    )
                    db.add(index)
                    db.commit()

                last_saved_date = db.query(HistoricalStockIndexData).filter_by(index_id=index.id).order_by(HistoricalStockIndexData.date.desc()).first()
                start_date = datetime(2010, 1, 1) if not last_saved_date else last_saved_date.date + timedelta(days=1)
                index_data = fdr.DataReader(index.symbol, start=start_date, end=datetime.now())
                for date, data in index_data.iterrows():
                    try:
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
                        batch.append(historical_index_data)
                        if len(batch) >= batch_size:
                            db.commit()
                            print(f"Batch committed for {index.symbol} index data")
                            batch = []
                    except Exception as e:
                        print(f"Error processing {date.date()} for {index_info['symbol']}: {e}")
            except Exception as e:
                print(f"Error saving historical data for {index_info['symbol']}: {e}")

        if batch:
            db.commit()
            print("Final batch committed for index data")

    except Exception as e:
        db.rollback()
        print(f"Error saving stock index data: {e}")
    finally:
        db.close()

def commodity_data_update():
    db = next(get_db())
    print("Updating commodity data...")
    
    # FRED에서 사용할 수 있는 원자재 심볼 (FRED의 코드로 교체 필요)
    commodities = [
        {'symbol': 'GOLDAMGBD228NLBM', 'name': 'Gold'},  # Gold
        {'symbol': 'SILVERPRICE', 'name': 'Silver'},  # Example symbol, replace with actual FRED code if needed
        {'symbol': 'DCOILWTICO', 'name': 'Crude Oil'},  # WTI Crude Oil
        {'symbol': 'DHHNGSP', 'name': 'Natural Gas'},  # Henry Hub Natural Gas Spot Price
        {'symbol': 'PCOPPUSDM', 'name': 'Copper'},  # Copper (FRED code needs verification)
        {'symbol': 'PLATINUM', 'name': 'Platinum'},  # Example symbol, replace with actual FRED code if needed
        {'symbol': 'PALLADIUM', 'name': 'Palladium'}  # Example symbol, replace with actual FRED code if needed
    ]

    try:
        batch_size = 100
        batch = []
        for commodity_info in commodities:
            try:
                # 데이터베이스에서 해당 원자재 조회 또는 생성
                commodity = db.query(Commodity).filter_by(symbol=commodity_info['symbol']).first()
                if not commodity:
                    commodity = Commodity(
                        symbol=commodity_info['symbol'],
                        name=commodity_info['name']
                    )
                    db.add(commodity)
                    db.commit()

                # 가장 최근 저장된 데이터 날짜 가져오기
                last_saved_date = db.query(HistoricalCommodityData).filter_by(commodity_id=commodity.id).order_by(HistoricalCommodityData.date.desc()).first()
                start_date = datetime(2000, 1, 1) if not last_saved_date else last_saved_date.date + timedelta(days=1)
                
                # FRED에서 데이터 가져오기
                commodity_data = pdr.DataReader(commodity.symbol, 'fred', start=start_date, end=datetime.now())

                # 데이터 처리 및 저장
                for date, row in commodity_data.iterrows():
                    try:
                        historical_commodity_data = db.query(HistoricalCommodityData).filter_by(commodity_id=commodity.id, date=date.date()).first()
                        if historical_commodity_data:
                            # 이미 존재하는 데이터 업데이트
                            historical_commodity_data.close = row[commodity.symbol]
                        else:
                            # 새로운 데이터 추가
                            historical_commodity_data = HistoricalCommodityData(
                                commodity_id=commodity.id,
                                date=date.date(),
                                close=row[commodity.symbol]
                            )
                            db.add(historical_commodity_data)
                        batch.append(historical_commodity_data)
                        if len(batch) >= batch_size:
                            db.commit()
                            print(f"Batch committed for {commodity.symbol} commodity data")
                            batch = []
                    except Exception as e:
                        print(f"Error processing {date.date()} for {commodity_info['symbol']}: {e}")
            except Exception as e:
                print(f"Error saving historical data for {commodity_info['symbol']}: {e}")

        # 남은 배치 커밋
        if batch:
            db.commit()
            print("Final batch committed for commodity data")

    except Exception as e:
        db.rollback()
        print(f"Error updating commodity data: {e}")
    finally:
        db.close()

def fetch_economic_data(api_key, series_id, start_date, end_date):
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        'series_id': series_id,
        'api_key': api_key,
        'file_type': 'json',
        'observation_start': start_date,
        'observation_end': end_date
    }
    response = requests.get(url, params=params)
    data = response.json()['observations']
    return [(d['date'], float(d['value'])) for d in data]

def update_economic_indicators():
    db = next(get_db())
    print("Updating Economic Indicators data...")
    try:
        load_dotenv()
        api_key = os.getenv('FRED_API')
        indicators = [
            {'type': 'Interest Rate', 'series_id': 'DFF'},
            {'type': 'CPI', 'series_id': 'CPIAUCSL'},
            {'type': 'Unemployment Rate', 'series_id': 'UNRATE'},
            {'type': 'GDP Growth Rate', 'series_id': 'GDP'}
        ]

        batch_size = 100
        batch = []
        for indicator in indicators:
            try:
                last_saved_date = db.query(EconomicIndicator).filter_by(indicator_type=indicator['type']).order_by(EconomicIndicator.date.desc()).first()
                start_date = '2010-01-01' if not last_saved_date else last_saved_date.date + timedelta(days=1)
                end_date = datetime.now().strftime('%Y-%m-%d')

                data = fetch_economic_data(api_key, indicator['series_id'], start_date, end_date)
                for date, value in data:
                    try:
                        existing_record = db.query(EconomicIndicator).filter_by(indicator_type=indicator['type'], date=date).first()
                        if existing_record:
                            existing_record.value = value  # 중복된 경우 값을 업데이트
                        else:
                            new_record = EconomicIndicator(
                                indicator_type=indicator['type'],
                                date=date,
                                value=value
                            )
                            db.add(new_record)  # 중복되지 않는 경우 새로 추가
                        batch.append((date, value))
                        if len(batch) >= batch_size:
                            db.commit()
                            print(f"Batch committed for {indicator['type']} economic data")
                            batch = []
                    except Exception as e:
                        print(f"Error processing {date} for {indicator['type']}: {e}")
            except Exception as e:
                print(f"Error updating data for {indicator['type']}: {e}")

        if batch:
            db.commit()
            print("Final batch committed for economic indicators data")

    except Exception as e:
        db.rollback()
        print(f"Error updating Economic Indicators: {e}")
    finally:
        db.close()