# 블로그 API 연동

import requests
from dotenv import load_dotenv
import os

load_dotenv()

TISTORY_ACCESS_TOKEN = os.getenv("TISTORY_ACCESS_TOKEN")
TISTORY_BLOG_NAME = os.getenv("TISTORY_BLOG_NAME")
TISTORY_API_POST_URL = "https://www.tistory.com/apis/post/write"


def upload_to_tistory(title: str, content: str, category_id: int = 0, visibility: int = 3) -> dict:
    """
    Tistory 블로그에 게시물 업로드
    :param title: 게시글 제목
    :param content: 게시글 본문 (HTML 허용)
    :param category_id: 카테고리 ID (기본값 0)
    :param visibility: 공개 범위 (0: 비공개, 1: 보호, 3: 발행)
    :return: 결과 딕셔너리
    """
    if not TISTORY_ACCESS_TOKEN or not TISTORY_BLOG_NAME:
        raise ValueError("TISTORY_ACCESS_TOKEN 또는 TISTORY_BLOG_NAME이 설정되지 않았습니다.")

    payload = {
        "access_token": TISTORY_ACCESS_TOKEN,
        "output": "json",
        "blogName": TISTORY_BLOG_NAME,
        "title": title,
        "content": content,
        "category": category_id,
        "visibility": visibility,
    }

    response = requests.post(TISTORY_API_POST_URL, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Tistory 업로드 실패: {response.status_code} - {response.text}")
