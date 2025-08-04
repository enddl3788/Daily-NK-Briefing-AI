# blog_uploader.py

import requests
from dotenv import load_dotenv
import os
import logging

# ✅ 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

TISTORY_ACCESS_TOKEN = os.getenv("TISTORY_ACCESS_TOKEN")
TISTORY_BLOG_NAME = os.getenv("TISTORY_BLOG_NAME")
TISTORY_API_POST_URL = "https://www.tistory.com/apis/post/write"

if not TISTORY_ACCESS_TOKEN:
    logger.warning("⚠️ TISTORY_ACCESS_TOKEN이 환경변수에 설정되어 있지 않습니다.")
if not TISTORY_BLOG_NAME:
    logger.warning("⚠️ TISTORY_BLOG_NAME이 환경변수에 설정되어 있지 않습니다.")

def upload_to_tistory(title: str, content: str, category_id: int = 0, visibility: int = 3) -> str:
    """
    Tistory 블로그에 게시물 업로드
    :param title: 게시글 제목
    :param content: 게시글 본문 (HTML 허용)
    :param category_id: 카테고리 ID (기본값 0)
    :param visibility: 공개 범위 (0: 비공개, 1: 보호, 3: 발행)
    :return: 게시글 URL 또는 오류 메시지
    """
    if not TISTORY_ACCESS_TOKEN or not TISTORY_BLOG_NAME:
        error_msg = "TISTORY_ACCESS_TOKEN 또는 TISTORY_BLOG_NAME이 설정되지 않았습니다."
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)

    logger.info("🚀 Tistory 블로그 업로드 시작")
    logger.info(f"📝 제목: {title}")
    logger.info(f"🔒 공개 범위: {visibility}, 카테고리 ID: {category_id}")

    payload = {
        "access_token": TISTORY_ACCESS_TOKEN,
        "output": "json",
        "blogName": TISTORY_BLOG_NAME,
        "title": title,
        "content": content,
        "category": category_id,
        "visibility": visibility,
    }

    try:
        response = requests.post(TISTORY_API_POST_URL, data=payload)
        response.raise_for_status()  # HTTP 오류가 있으면 예외 발생

        result = response.json()
        logger.info("✅ Tistory 업로드 성공")
        
        post_url = result.get("tistory", {}).get("url", "")
        if post_url:
            logger.info(f"🔗 게시글 URL: {post_url}")
        else:
            logger.warning("⚠️ 게시글 URL을 응답에서 찾지 못했습니다.")
        return post_url

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 요청 중 오류 발생: {e}")
        raise Exception(f"Tistory 업로드 실패: {str(e)}")
    except Exception as e:
        logger.error(f"❌ 기타 오류 발생: {e}")
        raise Exception(f"Tistory 업로드 실패: {str(e)}")
