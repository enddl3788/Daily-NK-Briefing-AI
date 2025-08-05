import logging
import requests
import os
from dotenv import load_dotenv

# ✅ 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

TISTORY_COOKIE = os.getenv("TISTORY_COOKIE")  # 수동으로 로그인 후 복사한 쿠키
TISTORY_BLOG = os.getenv("TISTORY_BLOG_NAME")  # 예: yourblog.tistory.com
TISTORY_CATEGORY_ID = os.getenv("TISTORY_CATEGORY_ID", "1193166")  # 기본값 0

def upload_to_tistory(title: str, content: str, category_id: int = 1193166, visibility: int = 20) -> dict:
    """
    티스토리 블로그에 게시글을 쿠키 기반으로 업로드합니다.
    :param title: 글 제목
    :param content: HTML 형식의 글 내용
    :param category_id: 카테고리 ID (기본: 0)
    :param visibility: 20 = 발행, 0 = 비공개
    :return: 응답 JSON 또는 에러 메시지 딕셔너리
    """
    logger.info("🛠 업로드 함수 호출됨")
    if not TISTORY_COOKIE or not TISTORY_BLOG:
        error_msg = "환경 변수 TISTORY_COOKIE 또는 TISTORY_BLOG가 누락되었습니다."
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)

    url = f"https://{TISTORY_BLOG}/manage/post.json"
    logger.info(f"🌐 요청 URL: {url}")

    headers = {
        "Host": TISTORY_BLOG,
        "Cookie": TISTORY_COOKIE,
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": f"https://{TISTORY_BLOG}/manage/newpost/",
        "Origin": f"https://{TISTORY_BLOG}",
        "Accept": "application/json, text/plain, */*"
    }
    logger.info(f"🔑 헤더에 Cookie 포함: {len(TISTORY_COOKIE)}자")

    data = {
        "id": "0",
        "title": title,
        "content": content,
        "slogan": title,
        "visibility": visibility,  # 20 = 공개, 0 = 비공개
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
        response = requests.post(url, headers=headers, json=data)
        logger.info(f"📥 응답 수신: 상태 코드 {response.status_code}")

        response.raise_for_status()

        res_json = response.json()
        logger.info(f"✅ 업로드 성공, 응답 데이터: {res_json}")

        return res_json

    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP 오류 발생: {e}")
        return {"error": str(e), "status_code": response.status_code if response else "N/A"}
    except Exception as e:
        logger.error(f"❌ 예외 발생: {e}")
        return {"error": str(e)}

def test_upload():
    title = "테스트 자동 업로드 글"
    content = """
    <h1>테스트 제목</h1>
    <p>이 글은 자동화 테스트용으로 작성되었습니다.</p>
    <pre><code class="language-python">print("Hello, Tistory!")</code></pre>
    """

    try:
        logger.info("테스트 업로드 시작")
        response = upload_to_tistory(title=title, content=content)
        logger.info(f"업로드 결과: {response}")
    except Exception as e:
        logger.error(f"업로드 중 예외 발생: {e}")

if __name__ == "__main__":
    test_upload()
