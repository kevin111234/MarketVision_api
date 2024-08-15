import pandas as pd
import requests
import re
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
import plotly.express as px
from collections import Counter
from konlpy.tag import Hannanum
from datetime import datetime
import time
import FinanceDataReader as fdr

import warnings
warnings.filterwarnings(action='ignore')
stock_name = "삼성전자"

hannanum=Hannanum()
df_krx=fdr.StockListing('KRX')
fu=UserAgent()
user=fu.random
headers={'User-Agent': user}

stock_num=df_krx[df_krx['Name']==stock_name]['Code'].values[0]
price=fdr.DataReader(stock_num).reset_index()[['Date','Close']]

columns=['Date','Close']+[ 'Top'+ str(i) for i in range(1,11)] + [ 'Main_News'+ str(i) for i in range(1,11)]
keyword=pd.DataFrame(columns=columns)

keyword['Date'] = price['Date']
keyword['Close']= price['Close']

def news_collector(search, media, make_date1, make_date2):
    part1="https://search.naver.com/search.naver?where=news&sm=tab_pge&query="
    part2="&sort=0&photo=0&field=0&pd=3&ds="
    
    date_1=f'{make_date1}&de={make_date1}'
    part3="&mynews=1&office_type=1&office_section_code=1&news_office_checked="
    part4="&nso=so:r,p:from"
    
    date_2=f'{make_date2}to{make_date2}'
    part5=",a:all&start="
    start_news_cnt='1'
    news_list=[]
    
    while start_news_cnt!='0':
        url=part1+search+part2+date_1+part3+media+part4+date_2+part5+start_news_cnt
        req = requests.get(url)
        html=req.text
        soup=bs(html, 'html.parser')
        nb=soup.select('div.sc_page > a')
        if len(nb) ==0: # 아예 검색결과가 없는 경우
            break 
        
        else:
            nb=nb[1] # 다음 페이지로 가는 버튼 (이전 페이지로 가는 버튼은 [0])
            if nb.attrs['aria-disabled']=='false': # 다음페이지로 넘어갈 수 있으면
                start_news_cnt=str(int(start_news_cnt)+10)
            else:
                start_news_cnt='0'
        

            req = requests.get(url)
            html=req.text

            soup=bs(html, 'html.parser')
            news=soup.select('div.group_news> ul.list_news > li div.news_area > div.news_info > div.info_group > a')

            for article in news:
                site_news=article.attrs['href']
                if 'n.news' in site_news:
                    each=requests.get(site_news, headers=headers)
                    news_html=each.text
                    soup=bs(news_html, 'html.parser')
                    content=str(soup.select('div#dic_area'))
                    content = re.sub('<.*?>', '', content)
                    content=content.replace("\n", '')
                    content=content.replace("\t", '')
                    content = re.sub(r'[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', content)
                    news_list.append(content) # 네이버 뉴스 본문 담기

        
    return news_list

def each_day_news(date):
    
    # 년월일 생성
    year=str(date.year)
    m=date.month
    d=date.day
    
    mm_=lambda m: str(m) if m>=10 else '0'+str(m)
    dd_=lambda m: str(d) if m>=10 else '0'+str(m)
    month=mm_(m)
    day=dd_(d)
    make_date1=year+'.'+month+'.'+day
    make_date2=year+month+day
    make_date3=year+'-'+month+'-'+day
    
    index_num=keyword[keyword['Date']==date].index.values[0]
    index_num
    
    # 매일경제: 1009
    # 이데일리: 1018
    # 한국경제: 1015
    # 헤럴드경제: 1016
    
    Maeil_economy=news_collector(stock_name, "1009", make_date1, make_date2)
    Edaily=news_collector(stock_name, "1018", make_date1, make_date2)
    Korea_economy=news_collector(stock_name, "1015", make_date1, make_date2)
    Herald_economy=news_collector(stock_name, "1016", make_date1, make_date2)
    
    words_list=[]
    media_s=[Maeil_economy,Edaily, Korea_economy, Herald_economy]

    for media in media_s:
        for news in media:
            words_list+=hannanum.nouns(news)

    over2=[ i for i in words_list if len(i) >1 ]
    
    count=Counter(over2)
    top10=count.most_common(10)
    
    if len(top10)<10:
        pass
        
    else:

        keyword.loc[index_num, 'Top1']=top10[0][0]
        keyword.loc[index_num, 'Top2']=top10[1][0]
        keyword.loc[index_num, 'Top3']=top10[2][0]
        keyword.loc[index_num, 'Top4']=top10[3][0]
        keyword.loc[index_num, 'Top5']=top10[4][0]
        keyword.loc[index_num, 'Top6']=top10[5][0]
        keyword.loc[index_num, 'Top7']=top10[6][0]
        keyword.loc[index_num, 'Top8']=top10[7][0]
        keyword.loc[index_num, 'Top9']=top10[8][0]
        keyword.loc[index_num, 'Top10']=top10[9][0]

        
    url="https://finance.naver.com/news/mainnews.naver?date="+make_date3
    req = requests.get(url)
    html=req.text
    soup=bs(html, 'html.parser')
    site_news=soup.select('ul.newsList > li.block1 > dl > dt > a')
    main_news=[] # 메인뉴스 제목을 담는 리스트
    for news in site_news:
        url="https://finance.naver.com"+news.attrs['href'] # 연결해줘야함
        req = requests.get(url)
        html=req.text
        soup=bs(html, 'html.parser')
        content=str(soup.select('div.article_info > h3'))
        content=re.sub('<.*?>', '', content)
        content=content.replace("\n", '')
        content=content.replace("\t", '')
        content= re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]','', content)
        content=content.replace("↓", '하락')
        content=content.replace("↑", '상승')
        res=content.strip()
        main_news.append(res)

    words_list=[]
    main_news=''.join(main_news)
    words_list=hannanum.nouns(main_news)

    over2=[ i for i in words_list if len(i) >1 ]

    count=Counter(over2)
    main10=count.most_common(10)
    
    if len(main10)<10:
        pass
        
    else:
        keyword.loc[index_num, 'Main_News1']=main10[0][0]
        keyword.loc[index_num, 'Main_News2']=main10[1][0]
        keyword.loc[index_num, 'Main_News3']=main10[2][0]
        keyword.loc[index_num, 'Main_News4']=main10[3][0]
        keyword.loc[index_num, 'Main_News5']=main10[4][0]
        keyword.loc[index_num, 'Main_News6']=main10[5][0]
        keyword.loc[index_num, 'Main_News7']=main10[6][0]
        keyword.loc[index_num, 'Main_News8']=main10[7][0]
        keyword.loc[index_num, 'Main_News9']=main10[8][0]
        keyword.loc[index_num, 'Main_News10']=main10[9][0]
        
    pass


list(map(each_day_news, keyword['Date']))