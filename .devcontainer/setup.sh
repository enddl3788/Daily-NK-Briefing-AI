#!/bin/bash

echo "🔧 Codespace 초기화 스크립트 실행 중..."

# .env 파일이 없으면 .env.example을 복사
if [ ! -f .env ]; then
  echo "📄 .env 파일 생성 중 (.env.example → .env)"
  cp .env.example .env
else
  echo "✅ .env 파일이 이미 존재합니다."
fi

echo "📦 Python 패키지 설치 중..."
pip install -r requirements.txt
