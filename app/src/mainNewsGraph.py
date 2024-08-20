from datetime import datetime
import FinanceDataReader as fdr

from mainNewsKeyword import each_day_news

date = datetime.now()
df_krx=fdr.StockListing('KRX')
stock_name = input("키워드를 입력해 주세요: ")

stock_num=df_krx[df_krx['Name']==stock_name]['Symbol'].values[0]
price=fdr.DataReader(stock_num).reset_index()[['Date','Close']]

each_day_news(stock_name, date)
