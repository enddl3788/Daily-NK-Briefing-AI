# summarizer.py
import os
import datetime
import logging
from typing import Optional, Tuple
from openai import OpenAI

# -----------------------------
# 로거 설정
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# -----------------------------
# OpenAI API 클라이언트 설정
# -----------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# 언어별 프롬프트 및 메타데이터 설정
# -----------------------------
LANGUAGES = {
    "ko": {
        "name": "긍정적 관점",
        "system_prompt": "당신은 긍정적 관점의 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 '북한 경제, 예상보다 성장세! 통계로 본 희망 신호'와 같은 제목을 생성해주세요.\n"
            "2. 북한의 최근 생산량 증가나 특정 산업의 발전을 중심으로 서술하고, 북한 경제의 긍정적인 측면을 부각하여 희망적인 톤으로 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    },
    "en": {
        "name": "부정적 관점",
        "system_prompt": "당신은 부정적 관점의 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 '북한 경제 성장률, 숨겨진 그림자는? 통계 이면의 현실'과 같은 제목을 생성해주세요.\n"
            "2. 식량난, 무역 적자, 경제난 등의 데이터를 중심으로 서술하고, 북한 경제의 부정적인 측면을 강조하여 비판적인 톤으로 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    },
    "zh": {
        "name": "미래 예측",
        "system_prompt": "당신은 미래 예측 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 '데이터로 예측하는 5년 뒤 북한 경제의 모습'과 같은 제목을 생성해주세요.\n"
            "2. 가능한 시나리오를 제시하고, 현재 데이터를 바탕으로 북한 경제의 향후 5년 변화를 예측하는 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    },
    "ja": {
        "name": "대외 관계",
        "system_prompt": "당신은 대외 관계 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 '북한 경제 성장이 남북 관계에 미치는 영향은?'과 같은 제목을 생성해주세요.\n"
            "2. 경제 데이터를 정치적 맥락과 연결하여 설명하고, 북한 경제 성장이 남북 관계나 국제 정세에 미치는 영향을 분석하는 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    },
    "ru": {
        "name": "카드 뉴스 형식",
        "system_prompt": "당신은 카드 뉴스 형식 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 '30초 만에 끝내는 북한 경제 핵심 브리핑'과 같은 제목을 생성해주세요.\n"
            "2. 각 문장이 짧고 명확하게 구성되도록 하고, 핵심 데이터만 뽑아서 간결하게 정리하는 카드 뉴스 형식의 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    },
    "de": {
        "name": "심층 분석",
        "system_prompt": "당신은 심층 분석 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 '북한의 식량 생산량, 통계의 진실은?'과 같은 제목을 생성해주세요.\n"
            "2. 세부적인 수치와 배경을 상세히 설명하고, 특정 데이터(예: 농업 생산량, 에너지 수급) 하나를 선택하여 심층적으로 분석하는 전문가 스타일의 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    },
    "fr": {
        "name": "Q&A 형식",
        "system_prompt": "당신은 Q&A 형식 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 '북한 경제에 대한 궁금증 5가지, 데이터를 통해 답하다'와 같은 제목을 생성해주세요.\n"
            "2. 독자들이 궁금해할 만한 북한 경제 관련 질문 3~4개를 선정하고, 데이터에 근거하여 답변하는 Q&A 형식의 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    },
    "es": {
        "name": "인포그래픽 설명",
        "system_prompt": "당신은 인포그래픽 설명 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 '인포그래픽으로 보는 북한 경제 현황'과 같은 제목을 생성해주세요.\n"
            "2. 데이터의 주요 포인트들을 명확한 문장으로 요약하고, 복잡한 통계 데이터를 시각적으로 설명하는 인포그래픽을 위한 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    },
    "ar": {
        "name": "초보자용",
        "system_prompt": "당신은 초보자용 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 '북한 경제, 10분 만에 이해하기'와 같은 제목을 생성해주세요.\n"
            "2. 북한 경제에 대해 전혀 모르는 초보자를 대상으로, 어려운 용어 없이 쉽고 재미있게 풀어 설명하는 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    },
    "hi": {
        "name": "전문가용",
        "system_prompt": "당신은 전문가용 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 '북한 경제 데이터 분석 보고서'와 같은 제목을 생성해주세요.\n"
            "2. 세부적인 통계 수치를 인용하고, 정책적 함의를 논하는 내용을 포함하여, 북한 전문가나 연구자를 위한 심도 깊은 분석 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    },
    "vi": {
        "name": "흥미 위주",
        "system_prompt": "당신은 흥미 위주 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 '북한에서 가장 잘 나가는 핫템은?'과 같이 독특한 제목을 생성해주세요.\n"
            "2. 흥미롭고 자극적인 제목과 내용을 포함하여 독자의 호기심을 유발하는 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    },
    "id": {
        "name": "결론 및 종합",
        "system_prompt": "당신은 결론 및 종합 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 하루 동안의 시리즈를 마무리하는 느낌으로, '오늘의 북한 경제: 데이터가 우리에게 말하는 것은?'과 같은 제목을 생성해주세요.\n"
            "2. 오늘 다룬 북한 경제 데이터의 모든 내용을 종합하고, 그 의미와 시사점을 분석하는 최종 결론 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    }
}


# -----------------------------
# 뉴스 요약 + HTML 변환 + 이미지 생성
# -----------------------------
def summarize_and_generate_image(
    text: str,
    model: str = "gpt-4o-mini",
    language: Optional[str] = None,
    image_size: str = "1024x1024"
) -> Tuple[str, str, Optional[str]]:
    """
    뉴스 텍스트를 받아 제목, HTML 본문, 이미지 URL을 생성합니다.
    """
    if not text.strip():
        return "", "<p>요약할 텍스트가 없습니다.</p>", None

    selected_lang = LANGUAGES.get(language, LANGUAGES["ko"])  # 기본값: 한국어
    system_message_content = selected_lang["system_prompt"]
    user_prompt_suffix_content = selected_lang["user_prompt_suffix"]
    title_prefix = selected_lang["title_prefix"]
    body_prefix = selected_lang["body_prefix"]
    
    logger.info(f"🌐 '{selected_lang['name']}'로 기사를 작성합니다.")

    # 사용자 요청 프롬프트
    full_user_prompt = f"{user_prompt_suffix_content}데이터:\n{text.strip()}"
    now = datetime.datetime.now()
    default_title = f"{now.strftime('%Y-%m-%d')} News Summary"

    try:
        # GPT로 뉴스 요약
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message_content},
                {"role": "user", "content": full_user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        full_response = response.choices[0].message.content.strip()
        logger.info("✅ 글 생성 완료. 길이: %d자", len(full_response))
        
        # 제목 / 본문 분리
        title_start = full_response.find(title_prefix)
        body_start = full_response.find(body_prefix)
        
        if title_start != -1 and body_start != -1:
            title_raw = full_response[title_start + len(title_prefix):body_start].strip()
            summary_raw = full_response[body_start + len(body_prefix):].strip()
            title = title_raw.strip('[]')
            summary = summary_raw.strip('[]')
        else:
            logger.warning("⚠️ 제목/본문 구분 실패. 전체 응답을 본문으로 처리합니다.")
            title = default_title
            summary = full_response

    except Exception as e:
        logger.error("❌ 글 생성 실패: %s", str(e))
        return "[오류]", f"<p>[글 생성 실패] {str(e)}</p>", None

    # HTML 보정
    if not any(tag in summary for tag in ['<p>', '<div>', '<ul>', '<ol>']):
        html_summary = f"<div>{summary.replace(chr(10), '<br/>')}</div>"
    else:
        html_summary = f"<div>{summary}</div>"

    # 이미지 생성
    image_url = None
    try:
        image_prompt = f"{title} — realistic news photo style, high quality, 4k, photograph, news style"
        img_response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size=image_size
        )
        image_url = img_response.data[0].url
        logger.info("🖼 이미지 생성 완료: %s", image_url)
    except Exception as e:
        logger.error("❌ 이미지 생성 실패: %s", str(e))
        image_url = None

    return title, html_summary, image_url


# -----------------------------
# 실행 테스트
# -----------------------------
if __name__ == "__main__":
    sample_text = "북한은 오늘 오전 단거리 탄도미사일을 동해상으로 발사했다고 한국 합참이 밝혔다. 이번 발사는 올해 들어 다섯 번째 무력 시위다."
    for lang_code in ["ko", "en", "ja"]:
        title, content, image = summarize_and_generate_image(sample_text, language=lang_code)
        print(f"=== [{LANGUAGES[lang_code]['name']}] ===")
        print("제목:", title)
        print("본문:", content)
        print("이미지 URL:", image)
        print()