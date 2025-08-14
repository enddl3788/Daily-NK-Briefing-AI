import requests
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Optional, Callable
from bs4 import BeautifulSoup

# ✅ 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ✅ API 키를 각 서비스에 맞게 별도로 설정
# 환경 변수에 각 API 키를 설정해주세요. (예: UNION_TREND_API_KEY, UNION_OTHBC_API_KEY 등)
API_ENDPOINTS = {
    "북한 동향": {
        "key": os.environ.get("UNION_API_KEY"),
        "url": "http://apis.data.go.kr/1250000/trend/getTrend",
        "parser": lambda item: {"title": item.get("sj", ""), "content": item.get("cn", "")},
        "params": {"cl": "ARGUMENT_DAIL"}
    },
    "김정은 공개 활동": {
        "key": os.environ.get("UNION_API_KEY"),
        "url": "http://apis.data.go.kr/1250000/othbcact/getOthbcact",
        "parser": lambda item: {
            "title": item.get("nes_cn", "")[:100],  # 제목은 보도내용의 앞부분 100자로 설정
            "content": (
                f"수행자: {item.get('execman', '정보 없음')}\n"
                f"보도일자: {item.get('nes_ymd', '정보 없음')}"
            )
        },
        "params": {}
    },
    "통일부 보도자료": {
        "key":os.environ.get("UNION_API_KEY"),
        "url": "http://apis.data.go.kr/1250000/nesdta/getNesdta",
        "parser": lambda item: {
            "title": item.get("sj", "").strip(), 
            "content": item.get("cn", "").strip() or item.get("sj", "").strip()
        },
        "params": {}
    }
}


def fetch_data_from_api(api_name: str, api_config: Dict[str, Any], start_date: str, end_date: str, max_items: int) -> Optional[str]:
    """
    단일 API에서 데이터를 가져오는 제네릭 함수입니다.
    """
    service_key = api_config["key"]
    base_url = api_config["url"]
    parser = api_config.get("parser")
    extra_params = api_config.get("params", {})

    if not service_key:
        logger.error(f"❌ '{api_name}' API 키가 설정되어 있지 않습니다.")
        return None

    # 모든 API에 공통적으로 적용되는 기본 파라미터
    params = {
        "serviceKey": service_key,
        "pageNo": 1,
        "numOfRows": max_items,
        "bgng_ymd": start_date,
        "end_ymd": end_date,
        "dataType": "JSON"
    }
    
    # API별 고유 파라미터 추가
    params.update(extra_params)
    
    try:
        logger.info(f"🔗 '{api_name}' API 요청 중...")
        # ✅ verify=True 또는 제거하여 SSL 검증 활성화
        response = requests.get(base_url, params=params) 
        response.raise_for_status()
        logger.info(f"✅ '{api_name}' API 응답 수신 완료")
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            logger.warning(f"⚠️ '{api_name}'에서 수신된 데이터가 없습니다.")
            return None
        
        logger.info(f"📦 '{api_name}' 수집된 항목 수: {len(items)}")

        combined_text = ""
        for item in items:
            # ✅ 각 API의 반환 형식에 맞는 파서를 사용하여 데이터 추출
            parsed_item = parser(item)
            title = parsed_item.get("title", "")
            content = parsed_item.get("content", "")
            combined_text += f"[{title}]\n{content}\n\n"
        
        return combined_text
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ '{api_name}' API 요청 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ '{api_name}' 처리 중 예외 발생: {e}")
        return None

def scrape_articles_from_unikorea(target_date: str) -> List[Dict[str, str]]:
    """
    통일부 북한정보포털에서 특정 날짜의 기사들을 스크랩합니다.
    """
    base_url = "https://nkinfo.unikorea.go.kr/nkp/trend/"
    list_url = f"{base_url}list.do"
    
    scraped_articles = []
    
    try:
        logger.info(f"🔗 통일부 북한정보포털에서 {target_date} 기사 스크랩 시작...")
        response = requests.get(list_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # <table>에서 등록일이 target_date인 행을 찾습니다.
        rows = soup.select('table tbody tr')
        
        for row in rows:
            date_td = row.select_one('td:nth-child(3)')
            if date_td and date_td.text.strip() == target_date:
                trend_mng_no_element = row.find('a', class_='trendViewBtn')
                if trend_mng_no_element:
                    trend_mng_no = trend_mng_no_element.get('trendmngno')
                    
                    if trend_mng_no:
                        article_url = f"{base_url}view.do?menuId=&trendMngNo={trend_mng_no}"
                        
                        logger.info(f"🔗 기사 본문 스크랩 중: {article_url}")
                        article_response = requests.get(article_url)
                        article_response.raise_for_status()
                        
                        article_soup = BeautifulSoup(article_response.text, 'html.parser')
                        
                        title_element = article_soup.find('h4', id='trendTtl')
                        content_element = article_soup.find('div', id='index')
                        
                        title = title_element.text.strip() if title_element else "제목 없음"
                        content = content_element.get_text(separator='\n', strip=True) if content_element else "내용 없음"
                        
                        scraped_articles.append({"title": title, "content": content})
                        logger.info(f"✅ 기사 스크랩 완료: '{title}'")
        
        if not scraped_articles:
            logger.warning(f"⚠️ {target_date}에 해당하는 기사가 없습니다.")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 웹 스크래핑 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ 스크래핑 중 예외 발생: {e}")
        return []

    return scraped_articles

def fetch_all_north_korea_trends(start_date=None, end_date=None, max_items=10) -> str:
    """
    정의된 3개의 API와 웹 스크래핑을 통해 최근 3일간의 데이터를 모두 가져와 합칩니다.
    """
    today = datetime.today()
    # 최근 3일간의 데이터를 가져오도록 시작일을 오늘 - 2일로 설정
    start_date_dt = today - timedelta(days=2)
    start_date = start_date_dt.strftime("%Y%m%d")
    end_date = today.strftime("%Y%m%d")

    logger.info(f"📡 API 및 스크래핑 동향 수집 시작: {start_date} ~ {end_date}")
    
    all_combined_text = ""
    
    # 1. API 데이터 수집
    for api_name, api_config in API_ENDPOINTS.items():
        api_text = fetch_data_from_api(api_name, api_config, start_date, end_date, max_items)
        if api_text:
            all_combined_text += f"\n\n--- '{api_name}' 데이터 시작 ---\n\n"
            all_combined_text += api_text
            all_combined_text += f"\n--- '{api_name}' 데이터 끝 ---\n"

    # 2. 스크래핑 데이터 수집
    scraped_data_found = False
    scraped_text = ""
    for i in range(3):
        target_date_dt = today - timedelta(days=i)
        target_date_str = target_date_dt.strftime("%Y.%m.%d.")
        
        scraped_articles = scrape_articles_from_unikorea(target_date_str)
        
        if scraped_articles:
            scraped_data_found = True
            scraped_text += f"\n\n--- '{target_date_str}' 스크랩 데이터 시작 ---\n\n"
            for article in scraped_articles:
                scraped_text += f"[{article['title']}]\n{article['content']}\n\n"
            scraped_text += f"\n--- '{target_date_str}' 스크랩 데이터 끝 ---\n"
    
    if scraped_data_found:
        all_combined_text += scraped_text
        
    if not all_combined_text.strip():
        logger.warning("⚠️ API 및 스크래핑 모두에서 데이터를 가져오지 못했습니다.")
        return "해당 기간에 대한 북한 동향 데이터가 없습니다."
        
    logger.info("📝 모든 API 및 스크래핑 데이터 병합 완료")
    return all_combined_text.strip()