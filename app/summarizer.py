import os
import logging
from openai import OpenAI
from typing import Tuple, Optional
import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    logger.error("❌ OPENAI_API_KEY가 설정되어 있지 않습니다.")
    raise EnvironmentError("OPENAI_API_KEY 환경변수가 없습니다.")

client = OpenAI(api_key=api_key)

# image_generation.generate_images 함수를 호출하는 가상 함수
# 실제 DALL-E 3 API를 사용하도록 이 부분을 수정해야 합니다.
def generate_image_from_text(prompt: str) -> Optional[str]:
    """
    텍스트 프롬프트를 사용하여 이미지를 생성하고 URL을 반환합니다.
    """
    try:
        logger.info("🎨 이미지 생성을 위해 DALL-E API를 호출합니다.")
        
        # 실제 OpenAI DALL-E 3 API 호출 코드를 활성화합니다.
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        # 생성된 이미지 URL을 반환합니다.
        return response.data[0].url
        
    except Exception as e:
        logger.error(f"❌ 이미지 생성 실패: {e}")
        return None

def summarize_text(text: str, model: str = "gpt-4") -> Tuple[str, str]:
    """
    텍스트 요약 및 제목 생성 → (제목, HTML 포맷 요약) 반환
    """
    if not text.strip():
        return "", "<p>요약할 텍스트가 없습니다.</p>"

    # 기존 프롬프트는 그대로 사용
    prompt = (
        "다음은 최신 북한 관련 뉴스 및 동향 데이터입니다. "
        "당신은 육하원칙과 역피라미드형 기사 작성법에 능숙한 전문 한국어 기자입니다.\n"
        "다음 요구사항에 맞춰 간결하고 객관적인 뉴스 기사를 작성해주세요:\n"
        "1. 내용을 한 문장으로 요약하는 간결한 제목을 생성해주세요.\n"
        "2. 역피라미드형 구조(중요한 내용을 먼저)에 따라 기사 본문을 작성해주세요.\n"
        "3. 제목과 기사 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해서 응답해주세요.\n"
        "4. 기사 본문은 html 기술을 활용하여 깔끔하게 작성해주세요.\n\n"
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
        
        title_start = full_response.find("제목: ")
        body_start = full_response.find("본문: ")
        
        if title_start != -1 and body_start != -1:
            title = full_response[title_start + len("제목:"):body_start].strip().strip('[]')
            summary = full_response[body_start + len("본문:"):].strip().strip('[]')
        else:
            title = default_title
            summary = full_response
            
    except Exception as e:
        logger.error("❌ 요약 실패: %s", str(e))
        return "[오류]", f"<p>[요약 실패] {str(e)}</p>"

    # 1. HTML 형식으로 변환
    html_summary = f"<div>{summary.replace(chr(10), '<br/>')}</div>"
    
    # 2. 이미지 생성을 위한 프롬프트 준비
    image_prompt = f"다음 제목과 본물을 참고하여 만화 스타일의 이미지를 생성해줘. 제목 : '{title}'. 본문 : {summary}" # 기사 제목을 기반으로 프롬프트 생성

    # 3. 이미지 생성 함수 호출
    image_url = generate_image_from_text(image_prompt)
    
    # 4. 이미지 생성에 성공했다면, HTML 본문에 이미지와 캡션 첨부
    if image_url:
        caption = f"본문을 요약한 AI 이미지"  # 캡션 텍스트 생성
        html_summary += (
            f'<div style="text-align: center; margin-top: 20px;">'
            f'<img src="{image_url}" alt="{caption}" style="max-width:100%; height:auto;">'
            f'<p style="font-size: 0.9em; color: #555;">{caption}</p>'  # 캡션 추가
            f'</div>'
        )
        logger.info("🖼️ 생성된 이미지와 캡션을 본문에 추가했습니다.")
    else:
        logger.warning("이미지 생성에 실패하여 이미지를 첨부하지 못했습니다.")
        
    return title, html_summary