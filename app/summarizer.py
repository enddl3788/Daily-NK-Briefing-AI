import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from typing import Tuple
import datetime

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("❌ OPENAI_API_KEY가 설정되어 있지 않습니다.")
    raise EnvironmentError("OPENAI_API_KEY 환경변수가 없습니다.")

client = OpenAI(api_key=api_key)

def summarize_text(text: str, model: str = "gpt-4") -> Tuple[str, str]:
    """
    텍스트 요약 및 제목 생성 → (제목, HTML 포맷 요약) 반환
    """
    if not text.strip():
        return "", "<p>요약할 텍스트가 없습니다.</p>"

    prompt = (
        "다음은 최신 북한 관련 뉴스 및 동향 데이터입니다. "
        "당신은 육하원칙과 역피라미드형 기사 작성법에 능숙한 전문 한국어 기자입니다.\n"
        "다음 요구사항에 맞춰 간결하고 객관적인 뉴스 기사를 작성해주세요:\n"
        "1. 내용을 한 문장으로 요약하는 간결한 제목을 생성해주세요.\n"
        "2. 역피라미드형 구조(중요한 내용을 먼저)에 따라 4~6문단 분량의 기사 본문을 작성해주세요.\n"
        "3. 제목과 기사 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해서 응답해주세요.\n"
        "4. [본문]은 html 언어를 사용하여 독자가 중요한 내용을 놓치지 않게 적극 활용해주세요.\n\n"
        "데이터:\n"
        + text.strip()
    )

    now = datetime.datetime.now()
    default_title = f"{now.strftime('%Y년 %m월 %d일')} 뉴스 요약"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "당신은 육하원칙과 역피라미드형 기사 작성법에 능숙한 전문 한국어 기자입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        full_response = response.choices[0].message.content.strip()
        logger.info("✅ 요약 완료. 길이: %d자", len(full_response))
        
        # 제목과 본문 분리
        title_start = full_response.find("제목: ")
        body_start = full_response.find("본문: ")
        
        if title_start != -1 and body_start != -1:
            # 제목 문자열 추출 후 '[]' 제거
            title = full_response[title_start + len("제목:"):body_start].strip().strip('[]')
            # 본문 문자열 추출 후 '[]' 제거
            summary = full_response[body_start + len("본문:"):].strip().strip('[]')
        else:
            title = default_title
            summary = full_response
            
    except Exception as e:
        logger.error("❌ 요약 실패: %s", str(e))
        return "[오류]", f"<p>[요약 실패] {str(e)}</p>"

    # HTML 형식으로 변환
    html_summary = f"<div>{summary.replace(chr(10), '<br/>')}</div>"
    
    return title, html_summary