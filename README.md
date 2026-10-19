GitHub 저장소: https://github.com/gaaaang/aimentoring
Streamlit 실행 페이지: https://ai-infra-tutor.streamlit.app/

# InfraMate - AI 인프라 용어 학습 튜터

대규모 언어 모델(LLM), 프롬프트 엔지니어링, Azure OpenAI, LangChain·LangGraph, RAG, 서비스 패키징, MCP·A2A 등 강의 내용을 바탕으로 만든 AI 인프라 용어 학습용 Streamlit 앱입니다.

## 주요 기능

- 역할, 학습 수준, 관심 분야에 맞춘 학습 경로 추천
- 68개의 AI 인프라 용어 카드와 한글·영문·약어 검색
- 정의, 쉬운 비유, AI 인프라에서의 역할, 실무 예시, 연관 용어
- 정답 여부와 답변 확신도를 함께 반영하는 맞춤형 퀴즈
- 틀린 문제 다시 보기, 분야별 진도 확인, 학습 기록 내려받기
- API 키 없이도 사용할 수 있는 내장형 학습 튜터
- OpenAI 또는 Azure OpenAI를 연결하면 AI 답변 모드 자동 활성화
- 외부 AI 서비스에 오류가 생기면 기본 학습 모드로 자동 전환

원본 강의 PDF는 공개 배포 파일에 포함하지 않았습니다. 앱에는 강의 주제를 바탕으로 새로 작성한 핵심 용어 카드만 담았습니다.

## Windows에서 바로 실행

`run_inframate.cmd`를 더블클릭하면 필요한 환경을 확인한 뒤 앱과 브라우저가 함께 열립니다. 실행 중에는 명령 창을 닫지 마세요. 명령 창을 닫으면 로컬 웹페이지 연결도 종료됩니다.

## 로컬 실행

Python 3.11 이상을 권장합니다.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501`을 엽니다.

## AI 답변 모드 설정

API 키가 없어도 모든 학습 기능을 사용할 수 있습니다. 생성형 AI 답변을 사용하려면 `.streamlit/secrets.toml.example`을 참고해 `.streamlit/secrets.toml`을 만들거나 배포 플랫폼의 비밀 설정(Secrets)에 값을 등록합니다.

OpenAI:

```toml
OPENAI_API_KEY = "..."
OPENAI_MODEL = "gpt-4.1-mini"
```

Azure OpenAI:

```toml
AZURE_OPENAI_API_KEY = "..."
AZURE_OPENAI_ENDPOINT = "https://<resource>.openai.azure.com"
AZURE_OPENAI_DEPLOYMENT = "<deployment-name>"
AZURE_OPENAI_API_VERSION = "<지원되는-api-version>"
```

API 키를 코드나 GitHub 저장소에 올리지 마세요.

## 테스트

```bash
python -m unittest discover -s tests -v
```

Streamlit 실행 후 상태 확인:

```text
http://localhost:8501/_stcore/health
```

## 프로젝트 구조

```text
ai-infra-tutor-agent/
├── streamlit_app.py
├── requirements.txt
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── src/
│   ├── knowledge.py
│   ├── quiz.py
│   └── tutor.py
└── tests/
    └── test_core.py
```

## 운영 확장 방향

- LangGraph 기반 설명·출제·평가·학습 계획 서브그래프
- 사내 문서 권한을 그대로 적용하는 하이브리드 검색 및 RAG
- Entra ID, RBAC, 프라이빗 엔드포인트, 관리형 ID 적용
- 사용자별 학습 진도와 복습 일정을 외부 데이터베이스에 영구 저장
- 검색·답변 품질 평가, 실행 경로 추적, 토큰 사용량·비용·응답 시간 모니터링

자세한 공개 배포 절차는 [DEPLOY.md](DEPLOY.md)를 참고하세요.

