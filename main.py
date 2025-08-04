# main.py

import logging
from fastapi import FastAPI, HTTPException
from app.fetcher import fetch_weekly_north_korea_trends
from app.summarizer import summarize_text
from app.blog_uploader import upload_to_tistory  # 블로그 자동 게시 기능
import asyncio

# ✅ 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="북한 브리핑 AI", description="주간 북한 동향 요약 챗봇(자동 뉴스 작성)", version="1.0")

@app.get("/")
def root():
    logger.info("루트 엔드포인트 '/' 접근")
    return {"message": "북한 브리핑 AI 서비스에 오신 것을 환영합니다."}

@app.get("/briefing/weekly")
async def get_weekly_briefing():
    logger.info("✅ /briefing/weekly 요청 수신")

    try:
        # 1. 최신 북한 동향 수집
        logger.info("📰 북한 동향 수집 시작")
        raw_data = fetch_weekly_north_korea_trends()

        if not raw_data:
            logger.warning("⚠️ 북한 동향 데이터 없음")
            raise HTTPException(status_code=404, detail="북한 동향 데이터를 불러오지 못했습니다.")

        # 2. 데이터 요약 처리
        logger.info("✍️  요약 처리 시작")
        summary = summarize_text(raw_data)

        logger.info("📦 요약 완료 및 응답 준비 완료")
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        logger.error(f"❌ 요약 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/briefing/publish")
async def publish_briefing():
    """
    요약한 내용을 블로그(예: Tistory)로 자동 발행
    """
    logger.info("✅ /briefing/publish 요청 수신")

    try:
        logger.info("📰 북한 동향 수집 시작")
        raw_data = fetch_weekly_north_korea_trends()

        logger.info("✍️ 요약 처리 시작")
        summary = summarize_text(raw_data)

        logger.info("🚀 블로그 업로드 시도")
        post_url = upload_to_tistory(title="주간 북한 동향 요약", content=summary)

        logger.info(f"✅ 게시 성공: {post_url}")
        return {
            "status": "published",
            "url": post_url
        }
    except Exception as e:
        logger.error(f"❌ 게시 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"게시 실패: {str(e)}")
