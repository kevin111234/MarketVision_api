import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from datetime import datetime, timedelta

def get_market_news(search_query, date=None):
    if not date:
        date = datetime.now()

    fu = UserAgent()
    user_agent = fu.random
    headers = {'User-Agent': user_agent}

    formatted_date = date.strftime('%Y.%m.%d')
    prev_day = (date - timedelta(days=1)).strftime('%Y.%m.%d')

    # URL 설정 (네이버 뉴스 검색 결과)
    url = f"https://search.naver.com/search.naver?where=news&query={search_query}&sm=tab_opt&sort=0&photo=0&field=0&reporter_article=&pd=3&ds={formatted_date}&de={formatted_date}&docid=&nso=so%3Ar%2Cp%3Afrom{formatted_date.replace('.','')}to{formatted_date.replace('.','')}&mynews=0&refresh_start=0&related=0"
    req = requests.get(url, headers=headers)
    soup = bs(req.text, 'html.parser')

    # 뉴스 제목과 링크 추출
    news_items = soup.select('.news_tit')
    news_list = []
    if news_items:
        for item in news_items[:10]:
            title = item.get_text(strip=True)
            link = item['href']
            news_list.append({'title': title, 'link': link})
    else:
        # 오늘 뉴스가 없을 경우 어제 뉴스 검색
        url = f"https://search.naver.com/search.naver?where=news&query={search_query}&sm=tab_opt&sort=0&photo=0&field=0&reporter_article=&pd=3&ds={prev_day}&de={prev_day}&docid=&nso=so%3Ar%2Cp%3Afrom{prev_day.replace('.','')}to{prev_day.replace('.','')}&mynews=0&refresh_start=0&related=0"
        req = requests.get(url, headers=headers)
        soup = bs(req.text, 'html.parser')
        news_items = soup.select('.news_tit')
        for item in news_items[:10]:
            title = item.get_text(strip=True)
            link = item['href']
            news_list.append({'title': title, 'link': link})

    return news_list

# 뉴스 추출 및 출력
keyword = input("키워드를 입력해주세요: ")

market_news = get_market_news(keyword)
if market_news:
    for index, news in enumerate(market_news):
        print(f"{index + 1}: {news['title']}")
        print(f"Link: {news['link']}\n")
else:
    print("No recent news found.")
