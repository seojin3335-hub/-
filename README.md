# AI 여행 영상 검색기 - 1차 MVP

## 현재 구현된 기능
- 웹 브라우저 UI
- 주제 입력
- YouTube Data API v3 검색
- 영상 제목/채널/게시일/길이/조회수/썸네일 표시
- 기본 관련도 점수로 정렬
- YouTube 원본 링크 열기
- 2번 자동편집기 연결 자리(다음 단계)

## 실행

1. Python 3.10+ 설치
2. Flask 설치:
   pip install flask
3. YouTube Data API v3 키를 발급
4. 환경변수 설정

Windows PowerShell:
$env:YOUTUBE_API_KEY="여기에_API_키"

macOS/Linux:
export YOUTUBE_API_KEY="여기에_API_키"

5. 실행:
python app.py

6. 브라우저에서:
http://127.0.0.1:8000

## 주의
현재 관련도 점수는 AI 모델이 아니라 제목/설명에 검색어가 얼마나 포함되는지와 조회수를 이용한 임시 점수입니다.
다음 단계에서 실제 AI 분석을 붙일 수 있습니다.

## 다음 개발 단계
- 검색 결과 품질 개선
- AI 주제 관련도 분석
- 여행/브이로그 필터
- 조회수 대비 업로드 기간 분석
- 쇼츠 소재 가능성 점수
- 후보 저장
- 2번 자동편집기와 연결
- 서버 배포 및 사용자 계정
