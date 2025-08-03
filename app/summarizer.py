# 텍스트 요약 로직

import openai
import os

# 환경변수에서 OPENAI_API_KEY를 가져오도록 설정
openai.api_key = os.getenv("OPENAI_API_KEY")


def summarize_text(text: str, model: str = "gpt-4") -> str:
    """
    주어진 텍스트를 요약하여 반환합니다.
    OpenAI GPT-4 모델을 사용합니다.

    Args:
        text (str): 원본 텍스트 (북한 동향 등)
        model (str): 사용할 모델명 (기본: gpt-4)

    Returns:
        str: 요약된 텍스트
    """

    if not text.strip():
        return "요약할 텍스트가 없습니다."

    prompt = (
        "다음은 북한 관련 뉴스 및 동향 데이터입니다. 이를 주간 요약 뉴스 형태로 "
        "3~5문단 분량의 간결하고 이해하기 쉬운 한국어 뉴스 기사로 작성해주세요:\n\n"
        f"{text.strip()}"
    )

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "당신은 시사 뉴스를 잘 요약하는 한국어 기자입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        summary = response.choices[0].message["content"].strip()
        return summary

    except Exception as e:
        return f"[요약 실패] {str(e)}"