from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .tasks import dollar_rate, ticker_update, stock_data_update, stock_index_update, commodity_data_update, update_dollar_index
from .database import get_db

def start_scheduler():
  scheduler = BackgroundScheduler()

  db_session = next(get_db())

  # 환율 데이터 업데이트 작업 - 매일 오후 1시에 실행
  scheduler.add_job(dollar_rate, CronTrigger(hour=13, minute=0), args=[db_session], id="dollar_rate")

  # 달러 인덱스 데이터 업데이트 작업 - 매일 오후 1시에 실행
  scheduler.add_job(update_dollar_index, CronTrigger(hour=13, minute=0), args=[db_session], id="dollar_index")

  # 원자재 데이터 업데이트 작업 - 매일 오후 1시 30분에 실행
  scheduler.add_job(commodity_data_update, CronTrigger(hour=13, minute=30), args=[db_session], id="commodity_data_update")

  # 주식 티커 데이터 업데이트 작업 - 매일 오후 2시에 실행
  scheduler.add_job(ticker_update, CronTrigger(hour=14, minute=0), args=[db_session], id="ticker_update")

  # 주식 데이터 업데이트 작업 - 매일 오후 2시 30분에 실행
  scheduler.add_job(stock_data_update, CronTrigger(hour=14, minute=30), args=[db_session], id="stock_data_update")

  # 주식 인덱스 데이터 업데이트 작업 - 매일 오후 4시에 실행
  scheduler.add_job(stock_index_update, CronTrigger(hour=16, minute=0), args=[db_session], id="stock_index_update")

  scheduler.start()
  print("Scheduler started and jobs added!")
