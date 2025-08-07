#!/bin/bash

set -e  # 오류 시 중단
set -x  # 실행되는 명령 로그 출력

echo "🔧 Codespace 초기화 스크립트 실행 중..."

echo "📦 Python 패키지 설치 중..."
pip install -r requirements.txt

echo "📦 시작: 패키지 설치 중..."
sudo apt-get update && sudo apt-get install -y \
    ca-certificates \
    libssl-dev \
    curl

echo "🐍 pip 패키지 업그레이드..."
pip install --upgrade pip requests urllib3 certifi

echo "✅ 개발 환경 준비 완료"