#!/bin/bash

echo "🔧 Codespace 초기화 스크립트 실행 중..."

# .env 파일이 없으면 생성
if [ ! -f .env ]; then
  echo "📄 .env 파일 생성 중 (.env.example → .env)"
  cp .env.example .env
else
  echo "✅ .env 파일이 이미 존재합니다."
fi

# 의존성 설치
echo "📦 requirements.txt 설치 중..."
pip install -r requirements.txt
