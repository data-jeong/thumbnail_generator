# 썸네일 생성기 (Thumbnail Generator)

블로그와 SNS를 위한 썸네일 이미지를 쉽게 생성할 수 있는 웹 애플리케이션입니다.

## 주요 기능

- 티스토리 썸네일 (230x300) 생성
- 인스타그램 썸네일 (1080x1080) 생성
- 이미지 비율 자동 유지
- 그라데이션 효과 추가 (인스타그램 썸네일)
- 자동 배경 생성 및 최적화

## 기술 스택

- Python
- Streamlit
- Pillow (PIL)
- NumPy

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/yourusername/thumbnail-generator.git
cd thumbnail-generator
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
streamlit run app.py
```

## 사용 방법

1. 웹 브라우저에서 `http://localhost:8501` 접속
2. 플랫폼 선택 (티스토리 또는 인스타그램)
3. 이미지 업로드
4. 그라데이션 효과 추가 여부 선택
5. "썸네일 생성" 버튼 클릭
6. 생성된 썸네일 다운로드

## 라이선스

MIT License 