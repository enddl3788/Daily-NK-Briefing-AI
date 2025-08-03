# API 키 등 설정

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAPI 인증키
UNION_API_KEY = os.getenv("UNION_API_KEY")

# 통일부 OpenAPI 엔드포인트 예시 (실제 URL로 교체 필요)
NK_TREND_API_URL = "https://www.unikorea.go.kr/api/nk-trend/list"

# 블로그 업로드 관련 (예: Tistory, Brunch 등 추후 확장 가능)
BLOG_PLATFORM = os.getenv("BLOG_PLATFORM", "tistory")  # 기본은 tistory로 지정

# 요약 문단 수 (예: summarizer.py에서 사용할 수 있음)
SUMMARY_PARAGRAPH_LIMIT = 3

# 기본 날짜 계산 함수
def get_default_date_range(days=7):
    """지난 N일간 날짜 범위를 반환"""
    today = datetime.today()
    start_date = today - timedelta(days=days)
    return start_date.strftime("%Y%m%d"), today.strftime("%Y%m%d")
