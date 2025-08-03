# FastAPI 실행

from fastapi import FastAPI, HTTPException
from app.fetcher import fetch_north_korea_trends
from app.summarizer import summarize_text
from app.blog_uploader import post_to_blog  # 블로그 자동 게시 기능
import asyncio

app = FastAPI(title="북한 브리핑 AI", description="주간 북한 동향 요약 챗봇(자동 뉴스 작성)", version="1.0")


@app.get("/")
def root():
    return {"message": "북한 브리핑 AI 서비스에 오신 것을 환영합니다."}


@app.get("/briefing/weekly")
async def get_weekly_briefing():
    try:
        # 1. 최신 북한 동향 수집
        raw_data = await fetch_north_korea_trends()
        if not raw_data:
            raise HTTPException(status_code=404, detail="북한 동향 데이터를 불러오지 못했습니다.")

        # 2. 데이터 요약 처리
        summary = summarize_text(raw_data)

        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/briefing/publish")
async def publish_briefing():
    """
    요약한 내용을 블로그(예: Tistory)로 자동 발행
    """
    try:
        raw_data = await fetch_north_korea_trends()
        summary = summarize_text(raw_data)

        post_url = post_to_blog(title="주간 북한 동향 요약", content=summary)
        return {
            "status": "published",
            "url": post_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"게시 실패: {str(e)}")
