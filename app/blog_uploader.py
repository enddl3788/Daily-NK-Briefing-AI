import logging
import requests
import os
from typing import Optional, Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 환경 변수에서 Tistory 정보 불러오기
TISTORY_COOKIE = os.environ.get("TISTORY_COOKIE")
TISTORY_BLOG_NAME = os.environ.get("TISTORY_BLOG_NAME")

def upload_to_tistory(
    title: str,
    content: str,
    language_code: str,
    category_map: Dict[str, int],
    visibility: int = 20
) -> Optional[str]:
    """
    Tistory 블로그에 게시글을 쿠키 기반으로 업로드합니다.
    
    :param title: 글 제목
    :param content: HTML 형식의 글 내용
    :param language_code: 글을 작성한 언어 코드 (예: 'ko', 'en')
    :param category_map: 언어 코드와 카테고리 ID를 매핑하는 딕셔너리
    :param visibility: 20 = 발행, 0 = 비공개, 1 = 보호, 2 = 친구 공개
    :return: 업로드된 글의 URL (성공 시) 또는 None (실패 시)
    """
    logger.info("🛠 업로드 함수 호출됨")

    if not TISTORY_COOKIE or not TISTORY_BLOG_NAME:
        error_msg = "환경 변수 TISTORY_COOKIE 또는 TISTORY_BLOG_NAME이 누락되었습니다."
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)

    # language_code를 기반으로 카테고리 ID 가져오기
    category_id = category_map.get(language_code)
    if category_id is None:
        error_msg = f"'{language_code}'에 해당하는 카테고리 ID를 찾을 수 없습니다."
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)

    url = f"https://{TISTORY_BLOG_NAME}/manage/post.json"
    logger.info(f"🌐 요청 URL: {url}")

    headers = {
        "Host": TISTORY_BLOG_NAME,
        "Cookie": TISTORY_COOKIE,
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": f"https://{TISTORY_BLOG_NAME}/manage/newpost/",
        "Origin": f"https://{TISTORY_BLOG_NAME}",
        "Accept": "application/json, text/plain, */*"
    }
    
    data = {
        "id": "0",
        "title": title,
        "content": content,
        "slogan": title,
        "visibility": visibility,
        "category": int(category_id),
        "tag": "",
        "published": 1,
        "password": "",
        "uselessMarginForEntry": 1,
        "daumLike": "401",
        "cclCommercial": 0,
        "cclDerive": 0,
        "thumbnail": None,
        "type": "post",
        "attachments": [],
        "recaptchaValue": "",
        "draftSequence": None
    }
    logger.info(f"✉️ 전송할 데이터 준비 완료: 제목='{title}', 카테고리={category_id}, 공개={visibility}")

    try:
        logger.info("📤 POST 요청 전송 중...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        logger.info(f"📥 응답 수신: 상태 코드 {response.status_code}")

        response.raise_for_status()
        res_json = response.json()
        
        # 수정된 성공 응답 확인 로직
        # 'url' 필드가 응답 JSON에 존재하는지 확인합니다.
        post_url = res_json.get('entryUrl')
        if post_url:
            logger.info(f"✅ 업로드 성공, 게시글 URL: {post_url}")
            return post_url
        else:
            # 예상치 못한 응답인 경우
            error_msg = f"Tistory API에서 예상치 못한 성공 응답을 받았습니다: {res_json}"
            logger.error(f"❌ {error_msg}")
            return None

    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP 오류 발생: {e}")
        logger.error(f"오류 응답: {response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 네트워크 또는 기타 요청 오류 발생: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ 예상치 못한 예외 발생: {e}")
        return None