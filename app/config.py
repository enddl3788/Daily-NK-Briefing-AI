# config.py

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# ✅ 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()
logger.info("🔧 .env 파일 로딩 완료")

# OpenAPI 인증키
UNION_API_KEY = os.getenv("UNION_API_KEY")
if UNION_API_KEY:
    logger.info("🔐 UNION_API_KEY 로드 완료")
else:
    logger.warning("⚠️ UNION_API_KEY가 설정되지 않았습니다.")

# 통일부 OpenAPI 엔드포인트 예시
NK_TREND_API_URL = "https://apis.data.go.kr/1250000/trend"
logger.info(f"🌐 NK_TREND_API_URL: {NK_TREND_API_URL}")

# 블로그 업로드 플랫폼 설정
BLOG_PLATFORM = os.getenv("BLOG_PLATFORM", "tistory")
logger.info(f"📝 BLOG_PLATFORM 설정: {BLOG_PLATFORM}")

# 요약 문단 수 설정
SUMMARY_PARAGRAPH_LIMIT = 3
logger.info(f"📄 SUMMARY_PARAGRAPH_LIMIT: {SUMMARY_PARAGRAPH_LIMIT} 문단")

# 기본 날짜 계산 함수
def get_default_date_range(days=7):
    """지난 N일간 날짜 범위를 반환"""
    today = datetime.today()
    start_date = today - timedelta(days=days)
    logger.info(f"📅 기본 날짜 범위 계산: {start_date.strftime('%Y%m%d')} ~ {today.strftime('%Y%m%d')}")
    return start_date.strftime("%Y%m%d"), today.strftime("%Y%m%d")
