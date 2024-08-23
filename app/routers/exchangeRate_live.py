# routers/exchange_rate.py
from fastapi import APIRouter, HTTPException
import requests
from bs4 import BeautifulSoup

router = APIRouter()

@router.get("/exchange-rate")
def get_exchange_rate():
    url = "https://finance.naver.com/marketindex/exchangeDegreeCountQuote.naver?marketindexCd=FX_USDKRW&page=1"

    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 에러가 발생했는지 확인

        # BeautifulSoup을 사용하여 HTML 파싱
        soup = BeautifulSoup(response.text, "html.parser")
        rate_element = soup.select_one("body > div > table > tbody > tr:nth-child(1) > td:nth-child(2)")

        if rate_element:
            exchange_rate = rate_element.text.strip()
            return {"exchange_rate": exchange_rate}
        else:
            raise HTTPException(status_code=404, detail="Exchange rate element not found")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data: {e}")
