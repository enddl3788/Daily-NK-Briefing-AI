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
        "name": "한국어",
        "system_prompt": "당신은 전문 한국어 뉴스 기자입니다. 북한 관련 뉴스를 정확하고 객관적으로 작성하세요.",
        "user_prompt_suffix": (
            "다음 요구사항에 맞춰 작성해주세요:\n"
            "1. 내용을 한 문장으로 요약하는 간결한 제목을 시스템 프롬프트에 맞게 생성해주세요.\n"
            "2. 시스템 프롬프트에 맞게 본문을 작성해주세요.\n"
            "3. 제목과 본문을 `제목: [제목]`과 `본문: [본문]` 형식으로 구분해주세요.\n"
            "4. 본문은 HTML을 사용해 깔끔하게 작성해주세요.\n\n"
        ),
        "title_prefix": "제목: ",
        "body_prefix": "본문: ",
    },
    "en": {
        "name": "English",
        "system_prompt": "You are a professional journalist. Write an accurate and objective news article about North Korea in English.",
        "user_prompt_suffix": (
            "Write the following requirements:\n"
            "1. Create a concise, one-sentence title that summarizes the content, following the system prompt.\n"
            "2. Write the body according to the system prompt.\n"
            "3. Separate the title and body using `Title: [title]` and `Body: [body]` format.\n"
            "4. Write the body cleanly using HTML.\n\n"
        ),
        "title_prefix": "Title: ",
        "body_prefix": "Body: ",
    },
    "zh": { # 중국어 (간체, 번체 통합)
        "name": "中文",
        "system_prompt": "你是一名专业记者，请用中文撰写一篇关于朝鲜的准确、客观的新闻报道。",
        "user_prompt_suffix": (
            "请根据以下要求撰写：\n"
            "1. 编写一个简洁的标题，用一句话概括内容，并遵循系统提示。\n"
            "2. 根据系统提示撰写正文。\n"
            "3. 使用“标题: [标题]”和“正文: [正文]”的格式分隔标题和正文。\n"
            "4. 使用HTML格式清晰地撰写正文。\n\n"
        ),
        "title_prefix": "标题: ",
        "body_prefix": "正文: ",
    },
    "ja": {
        "name": "日本語",
        "system_prompt": "あなたはプロのジャーナリストです。北朝鮮に関する正確で客観的なニュース記事を書いてください。",
        "user_prompt_suffix": (
            "以下の要件に従って作成してください：\n"
            "1. 内容を要約した簡潔なタイトルを1文で作成し、システムプロンプトに従ってください。\n"
            "2. システムプロンプトに従って本文を作成してください。\n"
            "3. タイトルと本文を「タイトル: [タイトル]」と「本文: [本文]」の形式で区切ってください。\n"
            "4. 本文はHTMLを使用してきれいに作成してください。\n\n"
        ),
        "title_prefix": "タイトル: ",
        "body_prefix": "本文: ",
    },
    "ru": {
        "name": "Русский",
        "system_prompt": "Вы профессиональный журналист. Напишите точную и объективную новостную статью о Северной Корее на русском языке.",
        "user_prompt_suffix": (
            "Напишите следующее:\n"
            "1. Создайте краткий заголовок, который суммирует содержание в одном предложении, следуя системному запросу.\n"
            "2. Напишите основной текст в соответствии с системным запросом.\n"
            "3. Разделите заголовок и основной текст, используя формат `Заголовок: [заголовок]` и `Текст: [текст]`.\n"
            "4. Напишите основной текст с использованием HTML.\n\n"
        ),
        "title_prefix": "Заголовок: ",
        "body_prefix": "Текст: ",
    },
    "de": {
        "name": "Deutsch",
        "system_prompt": "Sie sind ein professioneller Journalist. Schreiben Sie einen genauen und objektiven Nachrichtenartikel über Nordkorea auf Deutsch.",
        "user_prompt_suffix": (
            "Bitte erstellen Sie den folgenden Text:\n"
            "1. Erstellen Sie einen prägnanten, einzeiligen Titel, der den Inhalt zusammenfasst und den Systemanweisungen folgt.\n"
            "2. Schreiben Sie den Hauptteil gemäß den Systemanweisungen.\n"
            "3. Trennen Sie Titel und Hauptteil mit den Formaten `Titel: [Titel]` und `Text: [Text]`.\n"
            "4. Schreiben Sie den Hauptteil sauber mit HTML.\n\n"
        ),
        "title_prefix": "Titel: ",
        "body_prefix": "Text: ",
    },
    "fr": {
        "name": "Français",
        "system_prompt": "Vous êtes un journaliste professionnel. Rédigez un article précis et objectif sur la Corée du Nord en français.",
        "user_prompt_suffix": (
            "Rédigez le texte en respectant les exigences suivantes :\n"
            "1. Créez un titre concis en une seule phrase qui résume le contenu, en suivant les instructions du système.\n"
            "2. Rédigez le corps de l'article en suivant les instructions du système.\n"
            "3. Séparez le titre et le corps en utilisant les formats `Titre : [titre]` et `Corps : [corps]`.\n"
            "4. Rédigez le corps de l'article en utilisant du HTML pour une mise en page soignée.\n\n"
        ),
        "title_prefix": "Titre : ",
        "body_prefix": "Corps : ",
    },
    "es": {
        "name": "Español",
        "system_prompt": "Eres un periodista profesional. Escribe una noticia precisa y objetiva sobre Corea del Norte en español.",
        "user_prompt_suffix": (
            "Escribe siguiendo los siguientes requisitos:\n"
            "1. Crea un título conciso de una sola frase que resuma el contenido, siguiendo las instrucciones del sistema.\n"
            "2. Escribe el cuerpo del artículo según las instrucciones del sistema.\n"
            "3. Separa el título y el cuerpo usando el formato `Título: [título]` y `Cuerpo: [cuerpo]`.\n"
            "4. Escribe el cuerpo de forma clara usando HTML.\n\n"
        ),
        "title_prefix": "Título: ",
        "body_prefix": "Cuerpo: ",
    },
    "ar": {
        "name": "العربية",
        "system_prompt": "أنت صحفي محترف. اكتب مقالاً إخبارياً دقيقاً وموضوعياً عن كوريا الشمالية باللغة العربية.",
        "user_prompt_suffix": (
            "اكتب النص مع الالتزام بالمتطلبات التالية:\n"
            "1. قم بإنشاء عنوان موجز من جملة واحدة يلخص المحتوى، باتباع توجيهات النظام.\n"
            "2. اكتب النص الأساسي وفقاً لتوجيهات النظام.\n"
            "3. افصل العنوان عن النص الأساسي باستخدام التنسيق `عنوان: [عنوان]` و `نص: [نص]`.\n"
            "4. اكتب النص الأساسي بشكل أنيق باستخدام HTML.\n\n"
        ),
        "title_prefix": "عنوان: ",
        "body_prefix": "نص: ",
    },
    "hi": {
        "name": "हिन्दी",
        "system_prompt": "आप एक पेशेवर पत्रकार हैं। उत्तर कोरिया के बारे में सटीक और वस्तुनिष्ठ समाचार लेख हिंदी में लिखें।",
        "user_prompt_suffix": (
            "कृपया निम्नलिखित आवश्यकताओं के अनुसार लिखें:\n"
            "1. सिस्टम प्रॉम्प्ट के अनुसार, सामग्री को सारांशित करने वाला एक संक्षिप्त शीर्षक बनाएं।\n"
            "2. सिस्टम प्रॉम्प्ट के अनुसार मुख्य भाग लिखें।\n"
            "3. शीर्षक और मुख्य भाग को `शीर्षक: [शीर्षक]` और `मुख्य भाग: [मुख्य भाग]` प्रारूप का उपयोग करके अलग करें।\n"
            "4. मुख्य भाग को HTML का उपयोग करके स्पष्ट रूप से लिखें।\n\n"
        ),
        "title_prefix": "शीर्षक: ",
        "body_prefix": "मुख्य भाग: ",
    },
    "vi": {
        "name": "Tiếng Việt",
        "system_prompt": "Bạn là một nhà báo chuyên nghiệp. Hãy viết một bài báo chính xác và khách quan về Triều Tiên bằng tiếng Việt.",
        "user_prompt_suffix": (
            "Vui lòng viết theo các yêu cầu sau:\n"
            "1. Tạo một tiêu đề ngắn gọn tóm tắt nội dung trong một câu, tuân thủ lời nhắc hệ thống.\n"
            "2. Viết nội dung chính theo lời nhắc hệ thống.\n"
            "3. Tách tiêu đề và nội dung chính bằng định dạng `Tiêu đề: [tiêu đề]` và `Nội dung: [nội dung]`.\n"
            "4. Viết nội dung chính một cách rõ ràng bằng HTML.\n\n"
        ),
        "title_prefix": "Tiêu đề: ",
        "body_prefix": "Nội dung: ",
    },
    "id": {
        "name": "Bahasa Indonesia",
        "system_prompt": "Anda adalah seorang jurnalis profesional. Tulis artikel berita yang akurat dan objektif tentang Korea Utara dalam Bahasa Indonesia.",
        "user_prompt_suffix": (
            "Silakan tulis sesuai dengan persyaratan berikut:\n"
            "1. Buat judul singkat yang merangkum konten dalam satu kalimat, ikuti perintah sistem.\n"
            "2. Tulis isi utama sesuai dengan perintah sistem.\n"
            "3. Pisahkan judul dan isi utama menggunakan format `Judul: [judul]` dan `Isi: [isi]`.\n"
            "4. Tulis isi utama dengan bersih menggunakan HTML.\n\n"
        ),
        "title_prefix": "Judul: ",
        "body_prefix": "Isi: ",
    },
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