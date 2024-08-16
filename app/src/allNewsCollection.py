import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent

def get_us_stock_news():
    # User-Agent 설정
    fu = UserAgent()
    headers = {'User-Agent': fu.random}

    # 네이버 금융 뉴스 페이지 URL
    url = "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=403"
    response = requests.get(url, headers=headers)
    soup = bs(response.text, 'html.parser')

    # 뉴스 항목 추출
    news_items = soup.select('.articleSubject a')
    news_list = []
    for item in news_items:
        title = item.get_text(strip=True)
        link = "https://finance.naver.com" + item['href']
        news_list.append({'title': title, 'link': link})

    return news_list

# 뉴스 추출 및 출력
us_stock_news = get_us_stock_news()
for index, news in enumerate(us_stock_news):
    print(f"{index + 1}: {news['title']}")
    print(f"Link: {news['link']}\n")
