# Tech Blog Thumbnail Generator

블로그 썸네일을 자동으로 생성하는 Streamlit 애플리케이션입니다.

## 기능

- TISTORY (1200x600) 및 Instagram (1080x1080) 썸네일 생성
- 커스텀 제목, 부제목, 기술 스택 입력
- 그라데이션 배경
- PNG 형식으로 다운로드

## 설치 방법

1. 저장소 클론
```bash
git clone <repository-url>
cd thumbnail_generator
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
streamlit run app.py
```

## 사용 방법

1. 플랫폼 선택 (TISTORY 또는 Instagram)
2. 제목과 부제목 입력
3. 기술 스택 입력 (한 줄에 하나씩)
4. 기간 정보 입력
5. "썸네일 생성" 버튼 클릭
6. 생성된 썸네일 확인 및 다운로드

## 주의사항

- 기본 시스템 폰트를 사용합니다 (arial.ttf)
- 이미지 생성에는 약간의 시간이 소요될 수 있습니다
- 한글 텍스트가 깨질 경우 시스템에 한글 폰트 설치가 필요할 수 있습니다 