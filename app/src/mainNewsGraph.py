from datetime import datetime
from mainNewsKeyword import each_day_news

date = datetime.now()
keyword = input("키워드를 입력해 주세요: ")
each_day_news(keyword, date)