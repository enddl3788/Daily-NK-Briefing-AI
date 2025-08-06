import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from app.fetcher import fetch_all_north_korea_trends
from app.summarizer import summarize_text
from app.blog_uploader import upload_to_tistory

# ✅ 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="북한 브리핑 AI",
    description="주간 북한 동향 요약 챗봇(자동 뉴스 작성)",
    version="1.0"
)

# ✅ Jinja2 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 스케줄러 인스턴스 생성
scheduler = AsyncIOScheduler()

# 스케줄링할 함수 정의
async def schedule_publish():
    """
    오후 5시에 실행될 블로그 게시 작업
    """
    logger.info("⏱️ 스케줄된 자동 게시 작업 시작...")
    try:
        # 1. 북한 동향 수집
        logger.info("📰 북한 동향 수집 시작")
        raw_data = await run_in_threadpool(fetch_all_north_korea_trends)

        # 2. 요약 및 제목 생성
        logger.info("✍️ 요약 및 제목 생성 시작")
        title, summary_html = await run_in_threadpool(summarize_text, raw_data)

        # 3. 블로그 업로드
        logger.info(f"🚀 블로그 업로드 시도 - 제목: {title}")
        post_url = await run_in_threadpool(upload_to_tistory, title, summary_html)

        logger.info(f"✅ 게시 성공: {post_url}")
        return {
            "status": "published",
            "title": title,
            "url": post_url
        }

    except Exception as e:
        logger.error(f"❌ 게시 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"게시 실패: {str(e)}")

# 애플리케이션 시작 시 스케줄러 시작
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 애플리케이션 시작 - 스케줄러 등록")
    # 매일 오후 5시 0분에 schedule_publish 함수 실행
    scheduler.add_job(schedule_publish, 'cron', hour=17, minute=00)
    scheduler.start()

# 애플리케이션 종료 시 스케줄러 종료
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 애플리케이션 종료 - 스케줄러 종료")
    scheduler.shutdown()

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    """
    메인 페이지 UI를 제공합니다.
    """
    logger.info("루트 엔드포인트 '/' 접근 - UI 페이지 반환")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/briefing/weekly")
async def get_weekly_briefing():
    """
    주간 북한 동향을 수집하고 요약하여 반환합니다.
    """
    logger.info("✅ /briefing/weekly 요청 수신")

    try:
        logger.info("📰 북한 동향 수집 시작")
        # 비동기 함수가 아니므로 run_in_threadpool을 사용
        raw_data = await run_in_threadpool(fetch_all_north_korea_trends)

        if not raw_data:
            logger.warning("⚠️ 북한 동향 데이터 없음")
            raise HTTPException(status_code=404, detail="북한 동향 데이터를 불러오지 못했습니다.")

        logger.info("✍️ 요약 처리 시작")
        title, summary_html = await run_in_threadpool(summarize_text, raw_data)

        logger.info("📦 요약 완료 및 응답 준비 완료")
        return {
            "status": "success",
            "title": title,
            "summary": summary_html
        }

    except Exception as e:
        logger.error(f"❌ 요약 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/briefing/publish")
async def publish_briefing():
    """
    주간 북한 동향을 요약하고 블로그에 게시합니다.
    """
    logger.info("✅ /briefing/publish 요청 수신")

    try:
        # 1. 북한 동향 수집
        logger.info("📰 북한 동향 수집 시작")
        raw_data = await run_in_threadpool(fetch_all_north_korea_trends)

        # 2. 요약 및 제목 생성
        logger.info("✍️ 요약 및 제목 생성 시작")
        title, summary_html = await run_in_threadpool(summarize_text, raw_data)

        # 3. 블로그 업로드
        logger.info(f"🚀 블로그 업로드 시도 - 제목: {title}")
        post_url = await run_in_threadpool(upload_to_tistory, title, summary_html)

        logger.info(f"✅ 게시 성공: {post_url}")
        return {
            "status": "published",
            "title": title,
            "url": post_url
        }

    except Exception as e:
        logger.error(f"❌ 게시 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"게시 실패: {str(e)}")