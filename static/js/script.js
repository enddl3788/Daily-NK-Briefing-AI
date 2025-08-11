document.addEventListener('DOMContentLoaded', () => {
    // FastAPI 템플릿에서 전달받은 스케줄 정보를 사용하지 않고, 
    // main.py의 스케줄링 정보와 동일하게 하드코딩합니다.
    const languageSchedules = {
        "ko": { name: "긍정적 관점", hour: 21 },
        "en": { name: "부정적 관점", hour: 23 },
        "zh": { name: "미래 예측", hour: 1 },
        "ja": { name: "대외 관계", hour: 3 },
        "ru": { name: "카드 뉴스 형식", hour: 5 },
        "de": { name: "심층 분석", hour: 7 },
        "fr": { name: "Q&A 형식", hour: 9 },
        "es": { name: "인포그래픽 설명", hour: 11 },
        "ar": { name: "초보자용", hour: 13 },
        "hi": { name: "전문가용", hour: 15 },
        "vi": { name: "흥미 위주", hour: 17 },
        "id": { name: "결론 및 종합", hour: 19 },
    };

    const languageSelect = document.getElementById('languageSelect');
    const nextPublishTimeElement = document.getElementById('next-publish-time');
    const loadingElement = document.getElementById('loading');
    const resultElement = document.getElementById('result');
    const resultContentElement = document.getElementById('result-content');

    /**
     * 다음 게시 시간을 계산하고 화면에 표시하는 함수
     * main.py의 스케줄링 로직(매주 일요일, 특정 시간)을 반영합니다.
     */
    function updateNextPublishTime() {
        const selectedLangCode = languageSelect.value;
        const publishInfo = languageSchedules[selectedLangCode];

        if (!publishInfo) {
            nextPublishTimeElement.innerText = "스케줄 정보 없음";
            return;
        }

        const now = new Date();
        const currentDay = now.getDay(); // 0: 일요일, 1: 월요일, ...
        const currentHour = now.getHours();
        const publishDay = 0; // 스케줄은 매주 일요일에 실행됨

        let nextPublishDate = new Date();

        // 다음 게시일이 오늘(일요일)인지, 다음 주 일요일인지 판단
        if (currentDay > publishDay || (currentDay === publishDay && currentHour >= publishInfo.hour)) {
            // 오늘이 일요일이 아니거나, 오늘 일요일이고 게시 시간이 이미 지났다면 다음 주 일요일로
            const daysUntilNextSunday = (7 - currentDay) % 7 || 7; // 오늘이 일요일이면 7일 추가
            nextPublishDate.setDate(now.getDate() + daysUntilNextSunday);
        } else {
            // 오늘이 일요일이고 아직 게시 시간이 되지 않았다면 오늘로 설정
            const daysUntilThisSunday = (publishDay - currentDay + 7) % 7;
            nextPublishDate.setDate(now.getDate() + daysUntilThisSunday);
        }

        nextPublishDate.setHours(publishInfo.hour, 0, 0, 0);

        const days = ['일', '월', '화', '수', '목', '금', '토'];
        const dayName = days[nextPublishDate.getDay()];
        const formattedDate = `${nextPublishDate.getMonth() + 1}월 ${nextPublishDate.getDate()}일 (${dayName})`;
        const formattedTime = `${nextPublishDate.getHours()}시 0분`;
        
        nextPublishTimeElement.innerText = `${formattedDate} ${formattedTime} (언어: ${publishInfo.name})`;
    }

    // 언어 선택 시 다음 게시 시간 업데이트
    languageSelect.addEventListener('change', updateNextPublishTime);

    // 페이지 로드 시 초기 다음 게시 시간 표시
    updateNextPublishTime();

    /**
     * API 호출 및 결과 표시를 위한 일반 함수
     * @param {string} endpoint - 호출할 API 엔드포인트 URL
     */
    async function callApi(endpoint) {
        setLoading(true);
        const selectedLanguageCode = languageSelect.value;

        try {
            const response = await fetch(`${endpoint}?language=${encodeURIComponent(selectedLanguageCode)}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '알 수 없는 오류가 발생했습니다.');
            }

            displayResult(data, endpoint);
        } catch (error) {
            displayError(error.message);
        } finally {
            setLoading(false);
        }
    }

    function setLoading(isLoading) {
        if (isLoading) {
            loadingElement.style.display = 'block';
            resultElement.style.display = 'none';
        } else {
            loadingElement.style.display = 'none';
        }
    }

    function displayResult(data, endpoint) {
        resultElement.style.display = 'block';
        let displayContent = '';
        
        if (endpoint.includes('weekly')) {
            const imgTag = data.image_url ? 
                `<img src="${data.image_url}" alt="${data.title}" style="max-width:100%; height:auto; border-radius: 5px;">
                <div class="ai-image-note">AI가 생성한 이미지입니다.</div>` : 
                '';
            displayContent = `
                <h2>${data.title}</h2>
                <p><strong>언어:</strong> ${data.language_used || '기본 (한국어)'}</p>
                ${imgTag}
                <div>${data.summary}</div>
            `;
        } else if (endpoint.includes('publish')) {
            const imgTag = data.image_url ? 
                `<img src="${data.image_url}" alt="게시 이미지" style="max-width:100%; height:auto; margin-top:10px; border-radius: 5px;">` : 
                '';
            displayContent = `
                <h2>게시 성공! 🎉</h2>
                <p>글이 성공적으로 블로그에 게시되었습니다.</p>
                <p><strong>제목:</strong> ${data.title}</p>
                <p><strong>URL:</strong> <a href="${data.url}" target="_blank">${data.url}</a></p>
                <p><strong>언어:</strong> ${data.language_used || '기본 (한국어)'}</p>
                ${imgTag}
            `;
        }
        resultContentElement.innerHTML = displayContent;
    }

    function displayError(message) {
        resultElement.style.display = 'block';
        resultContentElement.innerHTML = `<p class="error">오류 발생: ${message}</p>`;
    }

    // 전역 함수로 등록하여 HTML에서 버튼 클릭 시 호출
    window.getBriefing = () => callApi('/briefing/weekly');
    window.publishBriefing = () => callApi('/briefing/publish');
});