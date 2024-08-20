import pandas as pd
import requests
import re
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
import plotly.express as px
from collections import Counter
from konlpy.tag import Hannanum
import FinanceDataReader as fdr
from datetime import datetime, timedelta

import warnings
warnings.filterwarnings(action='ignore')

hannanum = Hannanum() 

df_krx=fdr.StockListing('KRX')
fu=UserAgent()
user=fu.random
headers={'User-Agent': user}

def news_collector(search, media, make_date1, make_date2):
    part1 = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query="
    part2 = "&sort=0&photo=0&field=0&pd=3&ds="
    
    date_1 = f'{make_date1}&de={make_date1}'
    part3 = "&mynews=1&office_type=1&office_section_code=1&news_office_checked="
    part4 = "&nso=so:r,p:from"
    
    date_2 = f'{make_date2}to{make_date2}'
    part5 = ",a:all&start="
    start_news_cnt = '1'
    news_list = []
    
    while start_news_cnt != '0':
        url = part1 + search + part2 + date_1 + part3 + media + part4 + date_2 + part5 + start_news_cnt
        req = requests.get(url)
        html = req.text
        soup = bs(html, 'html.parser')
        news_items = soup.select('.news_contents')
        
        if len(news_items) == 0:  # 검색 결과가 없으면 종료
            break
        
        for item in news_items:
            title = item.select_one('.news_tit').get_text(strip=True)
            link = item.select_one('.news_tit')['href']
            news_list.append({'title': title, 'link': link})
        
        # 다음 페이지로 넘어가기
        next_button = soup.select_one('.btn_next')
        if next_button and 'href' in next_button.attrs:
            start_news_cnt = str(int(start_news_cnt) + 10)
        else:
            start_news_cnt = '0'
    return news_list



# 날짜 설정
def each_day_news(keyword, date):
  make_date1=date.strftime('%Y.%m.%d')
  make_date2=date.strftime('%Y%m%d')
  make_date3=date.strftime('%Y-%m-%d')

  # 매일경제: 1009
  # 이데일리: 1018
  # 한국경제: 1015
  # 헤럴드경제: 1016

  Maeil_economy=news_collector(keyword, "1009", make_date1, make_date2)
  Edaily=news_collector(keyword, "1018", make_date1, make_date2)
  Korea_economy=news_collector(keyword, "1015", make_date1, make_date2)
  Herald_economy=news_collector(keyword, "1016", make_date1, make_date2)

  words_list=[]
  media_s=[Maeil_economy,Edaily, Korea_economy, Herald_economy]
  words_list = []
  for media in media_s:
    for article in media:
      title = article['title']  # 사전에서 제목 추출
      words_list += hannanum.nouns(title)  # 제목에서 명사 추출

  over2=[ i for i in words_list if len(i) >1 ]
  count=Counter(over2)
  top10=count.most_common(10)

  url="https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=403&date="+make_date2
  req = requests.get(url)
  html=req.text
  soup=bs(html, 'html.parser')
  site_news=soup.select('.articleSubject a')

  main_news=[] # 메인뉴스 제목을 담는 리스트

  for news in site_news:
      content = news.get_text()  # 제목을 추출
      content = re.sub('<.*?>', '', content)
      content = content.replace("\n", '')
      content = content.replace("\t", '')
      content = re.sub(r'[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', content)
      content = content.replace("↓", '하락')
      content = content.replace("↑", '상승')
      res = content.strip()
      main_news.append(res)  # 제목을 리스트에 추가

  words_list=[]
  main_news=''.join(main_news)
  words_list=hannanum.nouns(main_news)

  over2=[ i for i in words_list if len(i) >1 ]

  count=Counter(over2)
  main10=count.most_common(10)

  return top10, main10

if __name__ == "__main__":
  date = datetime.now()
  keyword = input("키워드를 입력해 주세요: ")
  print(each_day_news(keyword, date))