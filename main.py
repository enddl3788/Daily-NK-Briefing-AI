# main.py
import logging
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Optional, List, Dict, Any

from app.fetcher import fetch_all_north_korea_trends
from app.summarizer import summarize_and_generate_image
from app.blog_uploader import upload_to_tistory
# summarizer.py에서 LANGUAGES 딕셔너리 가져오기 (main.py에서 직접 정의하는 대신 모듈에서 가져오는 것이 더 좋습니다.)
from app.summarizer import LANGUAGES as SUMMARIZER_LANGUAGES 

# -----------------------------
# 언어 및 카테고리 설정
# -----------------------------
# 언어 코드와 이름을 매핑하고 카테고리 ID를 추가합니다.
# NOTE: 이 딕셔너리는 summarizer.py에 정의되어 있으므로, 
# main.py에서는 import해서 사용하는 것이 좋습니다.
# 여기서는 예시로 다시 정의합니다.
SUMMARIZER_LANGUAGES = {
    "ko": {
        "name": "긍정적 관점",
        "code": "ko",
        "category_id": 1193166
    },
    "en": {
        "name": "부정적 관점",
        "code": "en",
        "category_id": 1193919
    },
    "zh": {
        "name": "미래 예측",
        "code": "zh",
        "category_id": 1193920
    },
    "ja": {
        "name": "대외 관계",
        "code": "ja",
        "category_id": 1193921
    },
    "ru": {
        "name": "카드 뉴스 형식",
        "code": "ru",
        "category_id": 1193922
    },
    "de": {
        "name": "심층 분석",
        "code": "de",
        "category_id": 1193923
    },
    "fr": {
        "name": "Q&A 형식",
        "code": "fr",
        "category_id": 1193924
    },
    "es": {
        "name": "인포그래픽 설명",
        "code": "es",
        "category_id": 1193925
    },
    "ar": {
        "name": "초보자용",
        "code": "ar",
        "category_id": 1193926
    },
    "hi": {
        "name": "전문가용",
        "code": "hi",
        "category_id": 1193929
    },
    "vi": {
        "name": "흥미 위주",
        "code": "vi",
        "category_id": 1193927
    },
    "id": {
        "name": "결론 및 종합",
        "code": "id",
        "category_id": 1193928
    },
}

# 지원하는 언어 코드를 리스트로 추출
SUPPORTED_LANGUAGES: List[str] = list(SUMMARIZER_LANGUAGES.keys())
# UI에 표시될 언어 이름을 리스트로 추출
LANGUAGE_NAMES: List[str] = [lang['name'] for lang in SUMMARIZER_LANGUAGES.values()]

# -----------------------------
# 로거 설정
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# -----------------------------
# FastAPI 애플리케이션 설정
# -----------------------------
app = FastAPI(
    title="북한 브리핑 AI",
    description="주간 북한 동향 요약 챗봇(자동 뉴스 작성)",
    version="1.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="static/templates")

scheduler = AsyncIOScheduler()

# -----------------------------
# 스케줄링 작업 함수
# -----------------------------
async def schedule_publish(language_code: str):
    """
    정기적으로 뉴스 데이터를 가져와 요약하고 블로그에 게시하는 함수
    """
    language_name = SUMMARIZER_LANGUAGES.get(language_code, {}).get("name", "기본")
    logger.info(f"⏱️ 스케줄된 자동 게시 작업 시작... (언어: {language_name}, 코드: {language_code})")
    try:
        logger.info("📰 북한 동향 수집 시작")
        raw_data = await run_in_threadpool(fetch_all_north_korea_trends)

        if not raw_data:
            logger.warning("⚠️ 북한 동향 데이터가 없어 스케줄 작업을 건너뜁니다.")
            return

        logger.info(f"✍️ 요약 및 이미지 생성 시작 (언어: {language_code})")
        title, summary_html, image_url = await run_in_threadpool(
            summarize_and_generate_image, raw_data, language=language_code
        )
        
        if not title or not summary_html:
            logger.error("❌ 요약 및 제목 생성 실패")
            return

        logger.info(f"🚀 블로그 업로드 시도 - 제목: {title}")
        
        # 이미지 URL이 있으면 HTML 본문에 추가
        full_summary_html = summary_html
        if image_url:
            full_summary_html = f'<img src="{image_url}" alt="{title}" style="max-width:100%; height:auto;"><br>{summary_html}'
        
        # 수정: upload_to_tistory 함수 호출 시 language_code와 category_map 전달
        category_map = {k: v['category_id'] for k, v in SUMMARIZER_LANGUAGES.items()}
        post_url = await run_in_threadpool(
            upload_to_tistory, title, f"{full_summary_html}", language_code, category_map
        )

        if post_url:
            logger.info(f"✅ 게시 성공: {post_url}")
        else:
            logger.error(f"❌ 게시 실패: post_url이 반환되지 않음")
        
    except Exception as e:
        logger.error(f"❌ 게시 실패: {str(e)}")
        pass

# -----------------------------
# 애플리케이션 라이프사이클 이벤트
# -----------------------------
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 스케줄러를 등록하고 실행합니다."""
    logger.info("🚀 애플리케이션 시작 - 다국어 스케줄러 등록")
    
    # 시간대별 게시 스케줄 (KST 기준)
    language_schedules = {
        "ko": 21,    
        "en": 23,    
        "zh": 1,    
        "ja": 3,    
        "ru": 5,    
        "de": 7,   
        "fr": 9,   
        "es": 11,   
        "ar": 13,
        "hi": 15,   
        "vi": 17,
        "id": 19,   
    }

    for language_code, hour in language_schedules.items():
        if language_code in SUMMARIZER_LANGUAGES:
            # 주간 스케줄링을 위한 `day_of_week` 파라미터를 추가했습니다.
            # 이 예시에서는 매주 일요일에 게시하도록 설정합니다. (0=월요일, 6=일요일)
            scheduler.add_job(
                schedule_publish,
                'cron',
                day_of_week='sun', 
                hour=hour,
                minute=0,
                args=[language_code]
            )
            language_name = SUMMARIZER_LANGUAGES[language_code]['name']
            logger.info(f"✅ 언어 '{language_name}' ({language_code}) 작업 등록: 매주 일요일 {hour}시 0분에 실행됩니다.")
        else:
            logger.warning(f"⚠️ 언어 코드 '{language_code}'는 지원되지 않아 스케줄링에서 제외됩니다.")

    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 스케줄러를 종료합니다."""
    logger.info("👋 애플리케이션 종료 - 스케줄러 종료")
    scheduler.shutdown()

# -----------------------------
# API 엔드포인트
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    """메인 페이지를 반환합니다."""
    logger.info("루트 엔드포인트 '/' 접근 - UI 페이지 반환")
    # jinja2 템플릿에 languages 딕셔너리를 직접 전달합니다.
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "languages": SUMMARIZER_LANGUAGES,
            "language_names": LANGUAGE_NAMES,
            "language_codes": SUPPORTED_LANGUAGES
        }
    )

@app.get("/briefing/weekly")
async def get_weekly_briefing(
    language: Optional[str] = Query(
        "ko",
        description="기사를 생성할 언어 코드",
        enum=SUPPORTED_LANGUAGES
    )
):
    """
    주간 북한 동향을 요약하여 반환합니다.
    """
    logger.info(f"✅ /briefing/weekly 요청 수신 (언어 코드: {language})")
    try:
        logger.info("📰 북한 동향 수집 시작")
        raw_data = await run_in_threadpool(fetch_all_north_korea_trends)

        if not raw_data:
            logger.warning("⚠️ 북한 동향 데이터 없음")
            raise HTTPException(status_code=404, detail="북한 동향 데이터를 불러오지 못했습니다.")

        logger.info("✍️ 요약 및 이미지 생성 시작")
        title, summary_html, image_url = await run_in_threadpool(
            summarize_and_generate_image, raw_data, language=language
        )

        logger.info("📦 요약 완료 및 응답 준비 완료")
        return {
            "status": "success",
            "title": title,
            "summary": summary_html,
            "image_url": image_url,
            "language_used": SUMMARIZER_LANGUAGES.get(language, {}).get("name", "기본")
        }

    except Exception as e:
        logger.error(f"❌ 요약 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/briefing/publish")
async def publish_briefing(
    language: Optional[str] = Query(
        "ko",
        description="게시할 기사의 언어 코드",
        enum=SUPPORTED_LANGUAGES
    )
):
    """
    주간 북한 동향을 요약하여 블로그에 게시합니다.
    """
    language_name = SUMMARIZER_LANGUAGES.get(language, {}).get("name", "기본")
    logger.info(f"✅ /briefing/publish 요청 수신 (언어: {language_name}, 코드: {language})")
    try:
        logger.info("📰 북한 동향 수집 시작")
        raw_data = await run_in_threadpool(fetch_all_north_korea_trends)

        if not raw_data:
            logger.warning("⚠️ 북한 동향 데이터 없음")
            raise HTTPException(status_code=404, detail="북한 동향 데이터를 불러오지 못했습니다.")

        logger.info("✍️ 요약 및 이미지 생성 시작")
        title, summary_html, image_url = await run_in_threadpool(
            summarize_and_generate_image, raw_data, language=language
        )

        logger.info(f"🚀 블로그 업로드 시도 - 제목: {title}")
        
        # 이미지 URL이 있으면 HTML 본문에 추가
        full_summary_html = summary_html
        if image_url:
            full_summary_html = f'<img src="{image_url}" alt="{title}" style="max-width:100%; height:auto;"><br>{summary_html}'
        
        # 수정: upload_to_tistory 함수 호출 시 language_code와 category_map 전달
        category_map = {k: v['category_id'] for k, v in SUMMARIZER_LANGUAGES.items()}
        post_url = await run_in_threadpool(
            upload_to_tistory, title, f"{full_summary_html}", language, category_map
        )

        if not post_url:
            raise Exception("블로그 게시 실패")

        logger.info(f"✅ 게시 성공: {post_url}")
        return {
            "status": "published",
            "title": title,
            "url": post_url,
            "image_url": image_url,
            "language_used": language_name
        }
    
    except Exception as e:
        logger.error(f"❌ 게시 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"게시 실패: {str(e)}")