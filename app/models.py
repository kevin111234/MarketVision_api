from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class Stock(Base):
    __tablename__ = 'stock'
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    industry_code = Column(String(20), nullable=False)
    industry = Column(String(100), nullable=False)
    exchange = Column(String(50), nullable=False)
    currency = Column(String(10), nullable=False)

    historical_data = relationship("HistoricalStockData", back_populates="stock")


class HistoricalStockData(Base):
    __tablename__ = 'historical_stock_data'
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)

    stock = relationship("Stock", back_populates="historical_data")
    __table_args__ = (UniqueConstraint('stock_id', 'date', name='stock_date_uc'),)


class StockIndex(Base):
    __tablename__ = 'stock_index'
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)

    historical_data = relationship("HistoricalStockIndexData", back_populates="index")


class HistoricalStockIndexData(Base):
    __tablename__ = 'historical_stock_index_data'
    id = Column(Integer, primary_key=True, index=True)
    index_id = Column(Integer, ForeignKey('stock_index.id'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=True)

    index = relationship("StockIndex", back_populates="historical_data")
    __table_args__ = (UniqueConstraint('index_id', 'date', name='index_date_uc'),)


class Commodity(Base):
    __tablename__ = 'commodity'
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)

    historical_data = relationship("HistoricalCommodityData", back_populates="commodity")


class HistoricalCommodityData(Base):
    __tablename__ = 'historical_commodity_data'
    id = Column(Integer, primary_key=True, index=True)
    commodity_id = Column(Integer, ForeignKey('commodity.id'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=True)

    commodity = relationship("Commodity", back_populates="historical_data")
    __table_args__ = (UniqueConstraint('commodity_id', 'date', name='commodity_date_uc'),)


class ExchangeRate(Base):
    __tablename__ = 'exchange_rate'
    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String(10), nullable=False)
    target_currency = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    close = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint('base_currency', 'target_currency', 'date', name='currency_date_uc'),)


class DollarIndex(Base):
    __tablename__ = 'dollar_index'
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)
    close = Column(Float, nullable=False)
