# fetcher.py

import requests
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Optional, Callable

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
        "key": os.environ.get("UNION_API_KEY"),
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


def fetch_all_north_korea_trends(start_date=None, end_date=None, max_items=10) -> str:
    """
    정의된 3개의 API에서 데이터를 모두 가져와 하나로 합칩니다.
    """
    if not start_date or not end_date:
        today = datetime.today()
        last_week = today - timedelta(days=3)
        start_date = last_week.strftime("%Y%m%d")
        end_date = today.strftime("%Y%m%d")

    logger.info(f"📡 모든 API 동향 수집 시작: {start_date} ~ {end_date}")
    
    all_combined_text = ""
    
    for api_name, api_config in API_ENDPOINTS.items():
        api_text = fetch_data_from_api(api_name, api_config, start_date, end_date, max_items)
        if api_text:
            all_combined_text += f"\n\n--- '{api_name}' 데이터 시작 ---\n\n"
            all_combined_text += api_text
            all_combined_text += f"\n--- '{api_name}' 데이터 끝 ---\n"
    
    if not all_combined_text.strip():
        logger.warning("⚠️ 모든 API에서 데이터를 가져오지 못했습니다.")
        return "해당 기간에 대한 북한 동향 데이터가 없습니다."
        
    logger.info("📝 모든 API 데이터 병합 완료")
    logger.info(all_combined_text.strip())
    return all_combined_text.strip()