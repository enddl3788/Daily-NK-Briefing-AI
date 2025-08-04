import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ✅ 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# OpenAI API 키 설정
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("❌ OPENAI_API_KEY가 설정되어 있지 않습니다.")
    raise EnvironmentError("OPENAI_API_KEY 환경변수가 없습니다.")

client = OpenAI(api_key=api_key)

def summarize_text(text: str, model: str = "gpt-4") -> str:
    """
    주어진 텍스트를 요약하여 반환합니다. OpenAI GPT-4 모델 사용.

    Args:
        text (str): 원본 텍스트
        model (str): 사용할 모델명 (기본값: gpt-4)

    Returns:
        str: 요약된 텍스트
    """
    if not text.strip():
        logger.warning("⚠️ 요약할 텍스트가 비어 있습니다.")
        return "요약할 텍스트가 없습니다."

    logger.info("✍️ 요약 요청 수신 - 토큰 길이: %d자", len(text.strip()))

    prompt = (
        "다음은 북한 관련 뉴스 및 동향 데이터입니다. 이를 주간 요약 뉴스 형태로 "
        "3~5문단 분량의 간결하고 이해하기 쉬운 한국어 뉴스 기사로 작성해주세요:\n\n"
        f"{text.strip()}"
    )

    try:
        logger.info("📤 OpenAI API 호출 시작")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "당신은 시사 뉴스를 잘 요약하는 한국어 기자입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        summary = response.choices[0].message.content.strip()
        logger.info("✅ 요약 완료 - 길이: %d자", len(summary))
        return summary

    except Exception as e:
        logger.error("❌ 요약 중 오류 발생: %s", str(e))
        return f"[요약 실패] {str(e)}"
