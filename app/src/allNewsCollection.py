import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qs, urlencode

def clean_link(url):
    # URL에서 article_id와 office_id를 추출하여 새로운 URL을 생성
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    article_id = query_params.get('article_id', [None])[0]
    office_id = query_params.get('office_id', [None])[0]

    # 새로운 URL 생성
    if article_id and office_id:
        cleaned_url = f"https://finance.naver.com/news/news_read.naver?article_id={article_id}&office_id={office_id}"
        return cleaned_url
    return url

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
        cleaned_link = clean_link(link)  # 링크 정리
        news_list.append({'title': title, 'link': cleaned_link})

    return news_list

# 뉴스 추출 및 출력
if __name__ == "__main__":
  us_stock_news = get_us_stock_news()
  for index, news in enumerate(us_stock_news):
      print(f"{index + 1}: {news['title']}")
      print(f"Link: {news['link']}\n")
