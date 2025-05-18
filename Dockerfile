# ✅ 1단계: Python 기반 이미지 사용
FROM python:3.11-slim

# ✅ 2단계: 작업 디렉토리 설정
WORKDIR /app

# ✅ 3단계: 종속성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ 4단계: 앱 소스 복사
COPY . .

# ✅ 5단계: Uvicorn으로 FastAPI 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
