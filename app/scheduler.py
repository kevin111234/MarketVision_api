from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .tasks import dollar_rate, ticker_update, stock_data_update, stock_index_update, commodity_data_update, update_dollar_index, update_economic_indicators

def start_scheduler():
  scheduler = BackgroundScheduler()

  # 환율 데이터 업데이트 작업 - 매일 오후 1시에 실행
  scheduler.add_job(dollar_rate, CronTrigger(hour=13, minute=0), id="dollar_rate")
  # 5분마다 실행
  # scheduler.add_job(dollar_rate, CronTrigger(minute='*/5'), id="dollar_rate_every_5min")

  # 달러 인덱스 데이터 업데이트 작업 - 매일 오후 1시에 실행
  scheduler.add_job(update_dollar_index, CronTrigger(hour=13, minute=0), id="dollar_index")
  # 5분마다 실행
  # scheduler.add_job(update_dollar_index, CronTrigger(minute='*/5'), id="dollar_index_every_5min")

  # 원자재 데이터 업데이트 작업 - 매일 오후 1시 30분에 실행
  scheduler.add_job(commodity_data_update, CronTrigger(hour=13, minute=30), id="commodity_data_update")
  # 5분마다 실행
  scheduler.add_job(commodity_data_update, CronTrigger(minute='*/5'), id="commodity_data_update_every_5min")

  # 주식 티커 데이터 업데이트 작업 - 매일 오후 2시에 실행
  scheduler.add_job(ticker_update, CronTrigger(hour=14, minute=0), id="ticker_update")
  # 5분마다 실행
  # scheduler.add_job(ticker_update, CronTrigger(minute='*/5'), id="ticker_update_every_5min")

  # 주식 데이터 업데이트 작업 - 매일 오후 2시 30분에 실행
  scheduler.add_job(stock_data_update, CronTrigger(hour=14, minute=30), id="stock_data_update")
  # 5분마다 실행
  # scheduler.add_job(stock_data_update, CronTrigger(minute='*/5'), id="stock_data_update_every_5min")

  # 주식 인덱스 데이터 업데이트 작업 - 매일 오후 4시에 실행
  scheduler.add_job(stock_index_update, CronTrigger(hour=16, minute=0), id="stock_index_update")
  # 5분마다 실행
  # scheduler.add_job(stock_index_update, CronTrigger(minute='*/5'), id="stock_index_update_every_5min")

  # 경제 지표 업데이트 작업 - 매일 오후 5시에 실행
  scheduler.add_job(update_economic_indicators, CronTrigger(hour=17, minute=0), id="economic_indicators_update")
  # 5분마다 실행
  # scheduler.add_job(update_economic_indicators, CronTrigger(minute='*/5'), id="economic_indicators_update_every_5min")

  scheduler.start()
  print("Scheduler started and jobs added!")