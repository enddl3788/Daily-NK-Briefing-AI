# OpenAPI 데이터 수집

import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

UNION_API_KEY = os.getenv("UNION_API_KEY")  # 통일부 OpenAPI 인증키
BASE_URL = "https://www.unikorea.go.kr/api/nk-trend/list"  # 예시: 실제 API 엔드포인트에 맞게 수정

def fetch_weekly_north_korea_trends(start_date=None, end_date=None, max_items=30):
    """
    통일부 OpenAPI에서 북한 주간 동향 데이터를 가져옵니다.

    Args:
        start_date (str): 조회 시작일 (yyyyMMdd)
        end_date (str): 조회 종료일 (yyyyMMdd)
        max_items (int): 가져올 데이터 최대 건수

    Returns:
        str: 수집된 텍스트 (뉴스 요약용)
    """
    if not start_date or not end_date:
        today = datetime.today()
        last_week = today - timedelta(days=7)
        start_date = last_week.strftime("%Y%m%d")
        end_date = today.strftime("%Y%m%d")

    params = {
        "serviceKey": UNION_API_KEY,
        "pageNo": 1,
        "numOfRows": max_items,
        "startCreateDt": start_date,
        "endCreateDt": end_date,
        "dataType": "JSON",
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])

        if not items:
            return "해당 기간에 대한 북한 동향 데이터가 없습니다."

        combined_text = ""
        for item in items:
            title = item.get("title", "")
            content = item.get("content", "")
            combined_text += f"[{title}]\n{content}\n\n"

        return combined_text.strip()

    except requests.exceptions.RequestException as e:
        return f"[데이터 요청 실패] {e}"
    except Exception as e:
        return f"[예외 발생] {e}"
