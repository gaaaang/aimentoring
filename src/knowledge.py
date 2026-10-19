"""Curated, deployment-safe knowledge cards for the tutor.

The cards are original summaries derived from the supplied course topics.  The
original lecture PDFs are intentionally not bundled with the public app.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Term:
    id: str
    name: str
    english: str
    category: str
    level: str
    summary: str
    definition: str
    analogy: str
    infra: str
    example: str
    related: tuple[str, ...]
    tags: tuple[str, ...]
    source: str
    reference_url: str = ""


def _t(
    id: str,
    name: str,
    english: str,
    category: str,
    level: str,
    summary: str,
    definition: str,
    analogy: str,
    infra: str,
    example: str,
    related: str,
    tags: str,
    source: str,
    reference_url: str = "",
) -> Term:
    return Term(
        id=id,
        name=name,
        english=english,
        category=category,
        level=level,
        summary=summary,
        definition=definition,
        analogy=analogy,
        infra=infra,
        example=example,
        related=tuple(x.strip() for x in related.split(",") if x.strip()),
        tags=tuple(x.strip() for x in tags.split(",") if x.strip()),
        source=source,
        reference_url=reference_url,
    )


TERMS: tuple[Term, ...] = (
    _t(
        "token", "토큰", "Token", "LLM 핵심", "입문", "언어 모델이 글을 읽고 생성할 때 사용하는 기본 단위",
        "문장 전체가 아니라 단어·부분 단어·기호로 나눈 작은 단위다. 모델 비용과 컨텍스트 길이는 보통 토큰 수를 기준으로 계산한다.",
        "문장을 레고 블록으로 분해했을 때의 블록 한 개와 같다.",
        "입력 제한, 응답 지연, API 비용을 결정하므로 게이트웨이에서 최대 입력 토큰을 관리해야 한다.",
        "‘AI infrastructure’라는 문장이 모델과 토크나이저에 따라 여러 토큰으로 나뉜다.",
        "컨텍스트 윈도우, 추론, 요청 한도", "tokenizer,비용,입력길이", "LLM Fundamentals",
    ),
    _t(
        "context-window", "컨텍스트 윈도우", "Context Window", "LLM 핵심", "입문", "모델이 한 번에 참고할 수 있는 정보의 최대 범위",
        "시스템 지침, 대화 기록, 검색 문서, 사용자 질문, 모델이 생성 중인 답변까지 모두 합쳐 모델이 한 번에 처리할 수 있는 토큰의 범위다.",
        "책상 위에 펼쳐 둘 수 있는 문서의 면적과 같다. 책상이 꽉 차면 일부를 치워야 한다.",
        "큰 윈도우는 편리하지만 지연과 비용이 커질 수 있어 요약·검색·메모리 정책이 필요하다.",
        "긴 매뉴얼 전체 대신 관련 단락 세 개만 검색해 프롬프트에 넣는다.",
        "토큰, RAG, 메모리", "context,문맥,길이", "LLM Fundamentals",
    ),
    _t(
        "inference", "추론", "Inference", "LLM 핵심", "입문", "학습된 모델이 입력을 받아 결과를 생성하는 실행 단계",
        "모델 가중치를 새로 학습하지 않고, 입력 토큰을 바탕으로 다음 토큰 확률을 계산해 응답을 만든다.",
        "요리법을 새로 배우는 과정이 학습이라면, 주문을 받고 실제 요리를 만드는 일이 추론이다.",
        "GPU/가속기 용량, 배치 크기, 캐시, 동시 요청 수가 처리량과 지연을 좌우한다.",
        "API 요청마다 모델 서버가 토큰을 순차 생성해 스트리밍한다.",
        "GPU, 지연시간, 처리량", "serving,latency,throughput", "LLM Fundamentals",
    ),
    _t(
        "temperature", "온도", "Temperature", "LLM 핵심", "입문", "모델 답변의 다양성을 조절하는 값",
        "낮으면 높은 확률의 토큰에 집중해 일관성이 커지고, 높으면 분포가 평평해져 표현이 다양해진다.",
        "정답을 고르는 모범생 모드와 아이디어를 넓게 내는 브레인스토밍 모드의 다이얼이다.",
        "용어 정의·채점은 낮게, 아이디어 생성은 다소 높게 설정하되 모델별 지원 범위를 확인한다.",
        "정확한 정의 생성은 0~0.3, 창의적 비유 생성은 더 높은 값으로 실험한다.",
        "Top-k, 추론, 환각", "sampling,무작위성", "LLM Fundamentals",
    ),
    _t(
        "structured-output", "구조화 출력", "Structured Output", "LLM 핵심", "중급", "모델의 답변을 정해진 데이터 구조로 받는 방식",
        "JSON Schema 같은 규칙으로 필드 이름, 자료형, 필수 항목을 정해 후속 프로그램이 응답을 안정적으로 처리할 수 있게 한다.",
        "자유 서술 답안 대신 정해진 칸이 있는 신청서를 받는 것과 같다.",
        "채점 결과, 라우팅 결정, API 인자는 스키마 검증 후 사용해야 장애와 보안 위험이 줄어든다.",
        "{score: 80, misconception: 'RAG와 학습 혼동', next_term: '임베딩'}처럼 채점한다.",
        "함수 호출, JSON Schema, 가드레일", "json,schema,파싱", "LLM Fundamentals",
    ),
    _t(
        "function-calling", "함수 호출", "Function Calling", "LLM 핵심", "중급", "언어 모델이 필요한 기능과 입력값을 고르는 기능",
        "개발자가 함수 이름과 설명, 입력값 규칙을 알려주면 모델이 어떤 함수를 어떤 값으로 호출할지 정리해 돌려준다. 실제 함수 실행은 애플리케이션이 담당한다.",
        "상담원이 요청을 이해해 알맞은 담당 부서와 접수 내용을 지정하는 것과 같다.",
        "도구 권한, 입력값 검증, 호출 시간 제한, 재시도, 감사 로그를 애플리케이션에서 관리한다.",
        "학습자가 '퀴즈 내줘'라고 하면 create_quiz(term='RAG', level='입문')를 선택한다.",
        "도구, MCP, 구조화 출력", "tool calling,api,스키마", "LLM Fundamentals",
    ),
    _t(
        "hallucination", "환각", "Hallucination", "LLM 핵심", "입문", "모델이 근거 없이 사실처럼 틀린 내용을 만드는 현상",
        "언어 모델은 사실을 직접 조회하고 검증하는 데이터베이스가 아니라, 문맥상 그럴듯한 다음 토큰을 예측하는 모델이다. 따라서 모르는 내용도 사실처럼 단정할 수 있다.",
        "기억이 흐릿한 사람이 빈칸을 그럴듯한 이야기로 채우는 것과 같다.",
        "검증된 자료를 RAG로 제공하고 출처 표시, 불확실성 안내, 결과 검증, 필요한 경우 사람의 승인을 함께 적용한다.",
        "존재하지 않는 GPU 제품 사양을 지어내지 않도록 공식 문서를 검색하고 근거를 표시한다.",
        "RAG, 가드레일, 평가", "오답,사실성,근거 기반 답변", "RAG 데이터 기반 AI의 활용",
    ),
    _t(
        "embedding", "임베딩", "Embedding", "RAG·데이터", "입문", "텍스트의 의미를 비교할 수 있도록 숫자 벡터로 바꾼 표현",
        "비슷한 의미의 문장들이 벡터 공간에서 가까워지도록 고차원 숫자 배열로 변환한다.",
        "뜻이 비슷한 책을 서점의 가까운 선반에 자동 배치하는 좌표와 같다.",
        "모델 차원, 입력 길이, 언어 성능, 비용을 비교하고 문서와 질문에 같은 임베딩 모델을 사용한다.",
        "'GPU 메모리' 질문과 'VRAM이 뭐야?' 문서를 의미상 가깝게 찾는다.",
        "벡터 데이터베이스, 유사도 검색, 문서 나누기 (청킹)", "vector,의미검색,embedding model", "RAG 데이터 기반 AI의 활용",
    ),
    _t(
        "rag", "RAG", "Retrieval-Augmented Generation", "RAG·데이터", "입문", "관련 자료를 찾아 참고 정보로 제공한 뒤 답을 만드는 방식",
        "질문과 관련된 외부 문서를 먼저 찾고, 그 내용을 프롬프트에 참고 정보로 넣어 최신성과 사실성을 높인다.",
        "외운 지식만 쓰는 시험이 아니라 필요한 교재를 찾아보는 오픈북 시험과 같다.",
        "수집·추출·분할·임베딩·인덱싱의 사전 단계와 검색·생성의 질의 단계를 각각 관측한다.",
        "사내 AI 인프라 표준 문서에서 근거 단락을 찾아 용어 설명과 출처를 제공한다.",
        "검색기, 임베딩, 벡터 데이터베이스", "검색증강생성,grounding,검색", "RAG 데이터 기반 AI의 활용",
    ),
    _t(
        "chunking", "문서 나누기 (청킹)", "Chunking", "RAG·데이터", "입문", "긴 문서를 검색하기 좋은 작은 단위로 나누는 과정",
        "고정 길이, 겹침, 문단, 의미, 코드 구조 등 문서 특성에 맞는 기준으로 텍스트 조각을 만든다.",
        "두꺼운 책에 장·절·문단별 색인을 붙이는 일과 같다.",
        "조각이 너무 작으면 앞뒤 맥락이 끊기고, 너무 크면 불필요한 내용까지 검색되어 비용이 늘어난다. 실제 질문으로 조각 크기와 겹침 범위를 평가해야 한다.",
        "용어 정의·주의점·예시가 함께 남도록 제목 기반으로 매뉴얼을 분할한다.",
        "임베딩, 메타데이터, RAG", "split,overlap,문서분할", "RAG 데이터 기반 AI의 활용",
    ),
    _t(
        "vector-db", "벡터 데이터베이스", "Vector Database", "RAG·데이터", "중급", "임베딩 벡터를 저장하고 의미가 비슷한 자료를 빠르게 찾는 저장소",
        "벡터와 원문·출처·카테고리 같은 메타데이터를 함께 저장하고 최근접 이웃 검색을 제공한다.",
        "책 제목이 아니라 내용의 의미로 찾을 수 있는 도서관 색인 시스템과 같다.",
        "데이터 규모, 필터, 지연, 백업, 권한, 여러 조직을 분리해 운영하는 기능을 기준으로 FAISS·Chroma·Qdrant·Milvus·관리형 서비스를 선택한다.",
        "GPU 관련 질문 벡터와 가까운 인프라 문서 조각 5개를 반환한다.",
        "HNSW, 임베딩, 검색기", "vector store,faiss,chroma,qdrant", "RAG 데이터 기반 AI의 활용",
    ),
    _t(
        "retriever", "검색기", "Retriever", "RAG·데이터", "중급", "질문과 관련된 문서 조각을 골라오는 검색 구성 요소",
        "벡터 유사도 검색에 키워드 검색, 조건 필터, 여러 형태의 질문, MMR, 유사도 기준값, 재정렬 등을 조합할 수 있다.",
        "도서관에서 질문을 듣고 가장 유용한 책과 쪽수를 찾아주는 사서와 같다.",
        "가져올 문서 수와 유사도 기준값을 고정하지 말고, 정답 문서 적중률과 응답 비용을 함께 측정해 조정한다.",
        "'PTU가 뭐야?' 질의를 확장해 Azure OpenAI 용량 문서를 우선 검색한다.",
        "RAG, 검색 결과 재정렬, 하이브리드 검색", "retrieval,top-k,mmr", "RAG 데이터 기반 AI의 활용",
    ),
    _t(
        "hybrid-search", "하이브리드 검색", "Hybrid Search", "RAG·데이터", "중급", "키워드 검색과 의미 검색을 결합하는 방식",
        "제품명이나 오류 코드를 정확히 찾는 키워드 검색과, 표현이 달라도 의미가 비슷한 자료를 찾는 벡터 검색 결과를 합친다.",
        "사람 이름은 명단에서 정확히 찾고, 관심사는 대화의 의미로 찾는 두 방법을 함께 쓰는 것이다.",
        "BM25 점수와 벡터 검색 점수의 범위를 맞춘 뒤, 실제 업무 질문으로 두 검색 방식의 반영 비율을 조정한다.",
        "‘429 TPM 초과’ 오류에서 정확한 오류 코드와 요청 한도의 의미를 함께 찾는다.",
        "검색기, 임베딩, 검색 결과 재정렬", "bm25,lexical,semantic", "RAG 데이터 기반 AI의 활용",
    ),
    _t(
        "hnsw", "HNSW", "Hierarchical Navigable Small World", "RAG·데이터", "고급", "계층 그래프로 빠른 근사 최근접 검색을 하는 인덱스",
        "상위 계층에서 큰 범위를 건너뛴 뒤 아래 계층으로 내려가며 가까운 벡터를 찾는다.",
        "고속도로로 목적지 근처까지 간 다음 큰길과 골목으로 좁혀가는 길찾기와 같다.",
        "정확도·메모리·인덱싱 시간·검색 속도의 균형을 ef, M 같은 설정값으로 조정한다.",
        "수백만 개 용어 문서에서 모든 벡터를 비교하지 않고 후보를 빠르게 찾는다.",
        "벡터 데이터베이스, 근사 최근접 이웃 검색(ANN), 플랫 인덱스", "그래프,인덱스,ann", "RAG 데이터 기반 AI의 활용",
    ),
    _t(
        "reranking", "검색 결과 재정렬", "Reranking", "RAG·데이터", "중급", "1차 검색 결과를 더 정교한 모델로 다시 정렬하는 단계",
        "빠른 검색기가 넓게 모은 후보를 더 정교한 모델이 다시 살펴보고, 질문과 직접 관련된 자료를 위로 올린다.",
        "서류 전형으로 후보를 모은 뒤 면접으로 최종 순위를 정하는 것과 같다.",
        "추가 지연과 비용이 생기므로 후보 수, 최종 문서 수, 캐싱을 실제 트래픽 기준으로 조절한다.",
        "상위 20개 검색 결과를 재정렬 모델이 5개로 추려 언어 모델에 전달한다.",
        "검색기, 컨텍스트 윈도우, 평가", "rank,cross encoder,post retrieval", "RAG 데이터 기반 AI의 활용",
    ),
    _t(
        "ai-agent", "AI 에이전트", "AI Agent", "에이전트·작업 흐름", "입문", "주어진 목표를 이루기 위해 상황을 파악하고 계획을 세워 도구를 사용하는 시스템",
        "언어 모델뿐 아니라 목표, 상태, 메모리, 도구, 실행 정책, 피드백 과정을 함께 갖춘 애플리케이션이다.",
        "목적지만 말하면 경로를 정하고 필요한 교통수단을 골라 이동하는 비서와 같다.",
        "자율성만 높이지 말고 권한 경계, 종료 조건, 비용 한도, 실패 복구, 인간 승인을 설계한다.",
        "튜터가 수준을 진단하고 적합한 용어를 설명한 뒤 퀴즈 결과로 다음 학습을 선택한다.",
        "도구, 상태, LangGraph", "agent,계획,자율", "LLM Fundamentals",
    ),
    _t(
        "tool", "도구", "Tool", "에이전트·작업 흐름", "입문", "에이전트가 외부 정보를 가져오거나 실제 작업을 수행할 때 사용하는 기능",
        "검색, 데이터베이스 조회, 계산, 티켓 생성처럼 입력과 출력이 분명한 실행 단위다.",
        "사람이 업무에 쓰는 검색창·계산기·전화기와 같은 손발이다.",
        "도구 설명과 입력값을 명확히 하고 최소 권한, 검증, 중복 실행 방지, 시간 제한, 감사 로그를 적용한다.",
        "get_term, create_quiz, save_progress를 각각 제한된 도구로 제공한다.",
        "함수 호출, MCP, AI 에이전트", "function,api,권한", "Azure OpenAI & LangChain",
    ),
    _t(
        "state", "상태", "State", "에이전트·작업 흐름", "중급", "작업 흐름을 실행하는 동안 각 단계가 함께 보고 갱신하는 데이터",
        "현재 단계, 메시지, 검색 결과, 점수, 재시도 수처럼 다음 행동을 결정하는 정보를 담는다.",
        "릴레이 경기에서 다음 주자에게 넘기는 바통과 경기 기록지의 결합이다.",
        "스키마와 갱신 규칙을 명시하고 민감정보·대용량 객체는 상태에 무분별하게 넣지 않는다.",
        "learner_level, current_term, quiz_score, misconceptions를 그래프 상태로 관리한다.",
        "LangGraph, 메모리, 체크포인트", "workflow,session,context", "Azure OpenAI & LangChain",
    ),
    _t(
        "memory", "메모리", "Memory", "에이전트·작업 흐름", "중급", "에이전트가 이전 대화와 정보를 필요할 때 다시 활용하도록 저장하는 기능",
        "최근 대화 내용, 대화 요약, 사용자 정보, 벡터 기반 장기 기억처럼 목적에 따라 저장 방식을 나눈다.",
        "현재 대화를 적는 메모지와 오래 보관하는 개인 학습 노트가 따로 있는 것과 같다.",
        "보존 기간, 개인정보, 사용자 분리, 삭제권, 요약 손실, 검색 품질을 함께 관리한다.",
        "틀린 용어와 이유를 저장해 다음 접속에서 복습 순서를 조정한다.",
        "상태, 체크포인트, 벡터 데이터베이스", "대화기록,장기기억,개인화", "Azure OpenAI & LangChain",
    ),
    _t(
        "langchain", "LangChain", "LangChain", "에이전트·작업 흐름", "입문", "언어 모델 기반 앱에서 모델·프롬프트·도구·검색 기능을 연결하기 쉽게 해주는 프레임워크",
        "서로 다른 모델과 데이터 소스를 공통 추상화로 연결하고 자주 쓰는 애플리케이션 컴포넌트를 제공한다.",
        "여러 제조사의 부품을 공통 규격으로 조립하게 해주는 어댑터 상자와 같다.",
        "편리한 추상화 아래의 실제 API와 데이터 흐름을 이해하고 버전 호환성을 고정·테스트한다.",
        "Azure OpenAI 모델과 검색기, 프롬프트 틀을 하나의 처리 흐름으로 묶는다.",
        "LangGraph, 검색기, 도구", "framework,chain,integration", "Azure OpenAI & LangChain",
    ),
    _t(
        "langgraph", "LangGraph", "LangGraph", "에이전트·작업 흐름", "중급", "상태와 조건에 따라 에이전트의 작업 흐름을 구성하는 프레임워크",
        "노드, 엣지, 조건부 라우팅, 반복, 병렬 실행, 체크포인트, 스트리밍을 명시적으로 설계한다.",
        "업무 담당자와 결재·반려·재작업 경로를 그린 프로세스 지도와 같다.",
        "무한 루프 방지, 최대 단계, 재시도, 상태 스키마, 중단·재개, 추적 가능성을 운영 요건으로 둔다.",
        "개념 설명→퀴즈 출제→채점→헷갈린 개념 확인 흐름을 점수에 따라 나눈다.",
        "상태, 서브그래프, 다중 에이전트", "graph,node,edge,workflow", "서비스 개발 및 패키징",
    ),
    _t(
        "multi-agent", "다중 에이전트", "Multi-Agent System", "에이전트·작업 흐름", "고급", "서로 다른 역할을 맡은 여러 에이전트가 협업하는 구조",
        "전문 역할을 분리해 각자 판단하고 결과를 공유하거나 검토하게 한다. 단일 에이전트보다 항상 좋은 것은 아니다.",
        "한 명의 만능 직원 대신 강사·출제자·채점자·코치가 팀으로 일하는 것과 같다.",
        "호출 수와 지연, 책임 경계, 충돌 해결, 공유 상태, 종료 조건을 설계하고 단일 흐름과 성능을 비교한다.",
        "설명 에이전트가 만든 내용을 검증 에이전트가 근거와 대조하고, 학습 계획 에이전트가 다음 용어를 추천한다.",
        "LangGraph, 서브그래프, A2A", "협업,role,orchestration", "서비스 개발 및 패키징",
    ),
    _t(
        "azure-openai", "Azure OpenAI", "Azure OpenAI Service", "클라우드·배포", "입문", "Azure 환경에서 OpenAI 모델을 배포·운영하는 관리형 서비스",
        "Azure 리소스, 지역, 모델 배포, 할당량, API 버전, 네트워크와 접근 제어를 결합해 기업용 언어 모델 API를 제공한다.",
        "OpenAI 모델에 Azure의 보안·네트워크·운영 관리 기능을 덧붙인 기업용 서비스와 같다.",
        "지역별 모델 제공 여부, 사설 네트워크, Entra ID·RBAC, 할당량, 콘텐츠 필터, 로그와 데이터 정책을 확인한다.",
        "사내 가상 네트워크(VNet)에서 프라이빗 엔드포인트를 통해 배포된 모델을 호출한다.",
        "모델 배포, 프라이빗 엔드포인트, API 버전", "aoai,azure,enterprise", "Azure OpenAI & LangChain",
    ),
    _t(
        "deployment", "모델 배포", "Model Deployment", "클라우드·배포", "입문", "특정 모델을 API로 호출할 수 있도록 이름과 처리 용량을 설정해 둔 운영 단위",
        "Azure OpenAI에서는 모델 자체의 이름과 별도로 ‘배포 이름’을 만들어 API 호출에 사용하며, 모델 버전·처리 용량·업데이트 정책도 함께 설정한다.",
        "창고의 제품 모델을 실제 판매 창구에 진열하고 창구 이름을 붙이는 것과 같다.",
        "개발·운영 환경 분리, 지역, 할당량, 버전 업그레이드, 이전 버전 복구, 트래픽 전환을 관리한다.",
        "gpt 계열 모델을 tutor-prod라는 배포 이름으로 만들어 앱 설정에 등록한다.",
        "엔드포인트, API 버전, PTU", "model serving,배포이름,capacity", "Azure OpenAI & LangChain",
    ),
    _t(
        "endpoint", "엔드포인트", "Endpoint", "클라우드·배포", "입문", "클라이언트가 서비스에 요청을 보내는 네트워크 주소",
        "프로토콜·호스트·경로로 구성되며 인증 정보와 함께 특정 API 기능에 접근하게 한다.",
        "건물 전체 주소와 그 안의 특정 접수 창구 번호를 합친 것과 같다.",
        "TLS, DNS, 사설·공용 네트워크 접근, 인증, 방화벽, 시간 제한, 상태 확인을 관리한다.",
        "https://example.openai.azure.com 같은 서비스 주소에 모델 배포와 API 경로를 붙인다.",
        "API 게이트웨이, 프라이빗 엔드포인트, 모델 배포", "url,api,network", "Azure OpenAI & LangChain",
    ),
    _t(
        "api-version", "API 버전", "API Version", "클라우드·배포", "중급", "사용할 API 계약과 기능 집합을 식별하는 버전",
        "같은 서비스라도 버전에 따라 요청 형식, 지원 모델·설정값·응답 항목이 달라질 수 있다.",
        "같은 기기의 충전 단자 규격이 세대마다 달라지는 것과 같다.",
        "SDK·프레임워크 호환성을 검증하고 버전을 명시적으로 고정한 뒤 업그레이드 회귀 테스트를 한다.",
        "알 수 없는 설정값 오류가 나면 Azure 배포와 코드의 API 버전을 함께 확인한다.",
        "Azure OpenAI, SDK, 모델 배포", "version,compatibility,preview", "Azure OpenAI & LangChain",
    ),
    _t(
        "rate-limit", "요청 한도", "Rate Limit", "클라우드·배포", "중급", "일정 시간 동안 처리할 수 있는 요청 수와 토큰 수의 한도",
        "RPM, TPM 같은 단위로 과부하와 공정한 자원 사용을 제어하며 초과 시 429 오류와 재시도 정보가 반환될 수 있다.",
        "놀이공원 입구가 분당 입장객 수를 제한하는 것과 같다.",
        "지수 백오프, 무작위 지연, 대기열, 캐시, 부하 분산, 사용자별 할당량과 모니터링을 사용한다.",
        "퀴즈 생성 요청이 몰리면 큐에 넣고 Retry-After를 따라 재시도한다.",
        "할당량, PTU, 오토스케일링", "rpm,tpm,429,throttling", "Azure OpenAI & LangChain",
    ),
    _t(
        "gpu", "GPU", "Graphics Processing Unit", "클라우드·배포", "입문", "대규모 병렬 계산에 강한 가속기",
        "행렬 연산을 동시에 많이 처리해 딥러닝 학습과 LLM 추론의 핵심 하드웨어로 쓰인다.",
        "한 문제를 빠르게 푸는 전문가 한 명보다 같은 계산을 동시에 하는 작업자 수천 명에 가깝다.",
        "VRAM, 대역폭, 전력·냉각, GPU 간 연결, 가용성, 비용, 사용률을 함께 살펴본다.",
        "모델 크기와 동시 사용자 수에 맞춰 GPU 인스턴스와 텐서 병렬화 방식을 선택한다.",
        "VRAM, 추론, 처리량", "accelerator,cuda,hardware", "AI 인프라 적용 확장",
    ),
    _t(
        "container", "컨테이너", "Container", "클라우드·배포", "입문", "앱과 의존성을 격리된 실행 단위로 묶는 기술",
        "호스트 운영체제의 커널을 공유하면서 코드·실행 환경·라이브러리·설정을 재현 가능한 이미지로 묶는다.",
        "어디로 옮겨도 같은 상태로 열리는 표준 화물 컨테이너와 같다.",
        "이미지 크기 최소화, 취약점 검사, 루트 권한 없이 실행, 배포 후 변경하지 않는 방식, 자원 제한, 비밀 정보 외부 관리를 적용한다.",
        "Streamlit 앱과 requirements.txt를 컨테이너 이미지로 만들고 개발·운영 환경에서 똑같이 실행한다.",
        "Kubernetes, Docker, 오토스케일링", "docker,image,runtime", "서비스 개발 및 패키징",
    ),
    _t(
        "autoscaling", "오토스케일링", "Autoscaling", "클라우드·배포", "중급", "부하에 따라 실행 자원을 자동으로 늘리거나 줄이는 기능",
        "CPU/GPU 사용률, 큐 길이, 요청 수 같은 지표와 정책으로 인스턴스 수 또는 용량을 조절한다.",
        "손님 수에 따라 계산대를 자동으로 열고 닫는 매장 운영과 같다.",
        "언어 모델은 처음 구동하거나 GPU를 확보하는 데 시간이 걸리므로, 최소 복제본 수와 예측 기반 확장, 대기열 제어가 중요하다.",
        "동시 학습자가 늘면 API 서버 복제본을 늘리고 한가할 때 줄인다.",
        "처리량, Kubernetes, 요청 한도", "scale,hpa,capacity", "AI 인프라 적용 확장",
    ),
    _t(
        "private-endpoint", "프라이빗 엔드포인트", "Private Endpoint", "보안·운영", "중급", "공용 인터넷을 거치지 않고 사설 네트워크에서 서비스에 접속하는 방식",
        "관리형 서비스에 가상 네트워크 내부의 사설 IP 주소를 할당해 공용 인터넷 노출을 줄인다.",
        "외부 정문 대신 회사 내부 전용 통로로 데이터센터에 들어가는 것과 같다.",
        "프라이빗 DNS, 서브넷, 네트워크 보안 그룹(NSG), 방화벽, 외부 통신 경로, 개발자 접속 경로를 함께 설계한다.",
        "Streamlit 백엔드가 가상 네트워크 연동을 통해 Azure OpenAI의 프라이빗 엔드포인트를 호출한다.",
        "VNet, 엔드포인트, RBAC", "network,private link,보안", "Azure OpenAI & LangChain",
    ),
    _t(
        "rbac", "RBAC", "Role-Based Access Control", "보안·운영", "입문", "역할에 따라 허용 작업을 부여하는 접근 제어",
        "사용자마다 권한을 직접 붙이기보다 관리자·개발자·조회자 같은 역할에 권한을 정의하고 구성원을 연결한다.",
        "건물의 직무별 출입증이 허용된 층만 열어주는 것과 같다.",
        "최소 권한, 업무 분리, 정기 검토, 임시 권한, 관리형 ID와 감사 로그를 사용한다.",
        "튜터 애플리케이션의 ID에는 모델 호출 권한만 주고, 리소스 삭제 권한은 주지 않는다.",
        "IAM, 관리형 ID, 비밀 정보 관리", "권한,role,least privilege", "Azure OpenAI & LangChain",
    ),
    _t(
        "secrets", "비밀 정보 관리", "Secrets Management", "보안·운영", "입문", "API 키·비밀번호·인증서 같은 민감한 값을 안전하게 보관하고 제공하는 방식",
        "비밀 정보를 코드나 저장소에 넣지 않고 전용 저장소나 배포 플랫폼 설정에 보관한 뒤, 실행 시점에 애플리케이션에 전달한다.",
        "현관 열쇠를 설계도에 인쇄하지 않고 금고에서 필요한 사람에게만 빌려주는 것과 같다.",
        "암호화, 접근 정책, 회전, 만료, 누출 탐지, 로그 마스킹을 적용한다.",
        "Streamlit Community Cloud의 비밀 설정에 API 키를 넣고, secrets.toml 파일은 Git에서 제외한다.",
        "RBAC, Key Vault, 환경변수", "api key,vault,credential", "서비스 개발 및 패키징",
    ),
    _t(
        "observability", "관측 가능성", "Observability", "보안·운영", "중급", "로그·메트릭·트레이스로 내부 상태를 추론할 수 있는 능력",
        "단순히 이상 여부만 확인하는 모니터링을 넘어, 입력·검색·모델·도구 중 어느 단계에서 품질이나 성능 문제가 생겼는지 추적할 수 있게 한다.",
        "차량의 경고등만 보는 것이 아니라 센서 기록과 주행 경로로 고장 원인을 찾는 것과 같다.",
        "요청 ID를 기준으로 검색 문서, 프롬프트 버전, 모델, 토큰, 응답 시간, 오류, 평가, 피드백을 연결하되 민감정보는 가린다.",
        "오답 신고 하나에서 사용된 문서와 모델 응답, 채점 결과를 끝까지 추적한다.",
        "실행 추적, 로깅, 평가", "모니터링,지표,추적", "서비스 개발 및 패키징",
    ),
    _t(
        "guardrail", "가드레일", "Guardrail", "보안·운영", "중급", "AI 입력·행동·출력을 정책 범위 안에 두는 통제 장치",
        "금칙어 필터 하나가 아니라 입력 검사, 도구 권한, 스키마 검증, 근거 확인, 콘텐츠 안전, 인간 승인을 포함한다.",
        "도로의 가드레일·신호·속도 제한이 함께 사고 위험을 줄이는 것과 같다.",
        "정책 우회 시험, 오탐·미탐 측정, 실패했을 때의 안전한 응답, 감사 가능성을 설계한다.",
        "근거 없는 인프라 명령은 실행하지 않고 설명과 공식 문서 링크만 제공한다.",
        "프롬프트 주입 공격, RBAC, 구조화 출력", "안전,정책,필터", "Prompt Engineering",
    ),
    _t(
        "prompt-injection", "프롬프트 주입 공격", "Prompt Injection", "보안·운영", "중급", "입력이나 문서에 악성 지시를 숨겨 모델의 원래 규칙을 바꾸려는 공격",
        "공격 지시는 사용자 질문뿐 아니라 웹페이지나 검색 문서에도 숨어 있을 수 있으며, 모델이 시스템 지침을 무시하거나 권한 있는 도구를 악용하도록 유도한다.",
        "참고 서류 안에 '이전 규칙을 무시하라'는 가짜 결재 지시를 끼워 넣는 것과 같다.",
        "지시와 데이터를 분리하고 외부 문서는 신뢰할 수 없는 입력으로 취급하며, 도구 허용 목록·최소 권한·출력 검증·승인을 적용한다.",
        "RAG 문서의 '비밀키를 출력하라'는 문장을 정보가 아닌 공격 문자열로 취급한다.",
        "가드레일, RAG, 도구", "jailbreak,security,untrusted data", "Prompt Engineering",
    ),
    _t(
        "mcp", "MCP", "Model Context Protocol", "프로토콜", "중급", "AI 애플리케이션이 외부 자료와 도구를 표준 방식으로 연결하도록 돕는 프로토콜",
        "MCP 호스트가 여러 클라이언트를 관리하고, 각 클라이언트는 서버에 연결해 서버가 제공하는 프롬프트·자료·도구를 확인하고 사용한다.",
        "서비스마다 제각각인 연결 방식을 하나의 공통 커넥터 규격으로 통일한 것과 같다.",
        "연결할 서버의 신뢰성, 권한 범위, 사용자 승인, 전송 보안, 도구 입력값 검증, 감사 로그를 확인한다.",
        "튜터가 사내 용어집 MCP 서버에서 자료를 읽고 퀴즈 생성 도구를 호출한다.",
        "도구, 자료, A2A", "model context protocol,host,client,server", "MCP·A2A의 이해와 실습",
    ),
    _t(
        "a2a", "A2A", "Agent-to-Agent Protocol", "프로토콜", "고급", "서로 내부 구현이 다른 에이전트들이 협업하도록 하는 통신 프로토콜",
        "에이전트 카드로 상대의 역량을 확인하고, 작업·메시지·결과물·진행 상태를 표준 형식으로 주고받는다.",
        "서로 다른 회사의 전문팀이 표준 업무 의뢰서와 상태표로 협업하는 것과 같다.",
        "상대 에이전트의 신원과 권한, 공유할 데이터 범위, 장기 작업의 상태 관리, 실패·취소 처리, 사용자 화면 표시 방식을 설계한다.",
        "인프라 튜터가 비용 최적화 전문 에이전트에게 분석 작업을 맡기고, 받은 결과를 학습 설명으로 바꾼다.",
        "MCP, 다중 에이전트, 에이전트 카드", "agent to agent,protocol,task", "MCP·A2A의 이해와 실습",
    ),
)

# The extended catalog is kept separately so the original course-aligned cards
# remain easy to review. Every added card points to an official reference.
from .expanded_terms import EXPANDED_TERM_ROWS

TERMS = TERMS + tuple(_t(*row) for row in EXPANDED_TERM_ROWS)


CATEGORIES: tuple[str, ...] = tuple(dict.fromkeys(t.category for t in TERMS))
LEVELS: tuple[str, ...] = ("입문", "중급", "고급")
TERM_BY_ID = {term.id: term for term in TERMS}

ALIASES: dict[str, str] = {
    "검색증강생성": "rag retrieval augmented generation",
    "벡터디비": "벡터 db vector database",
    "벡터 데이터베이스": "벡터 db vector database",
    "문맥창": "컨텍스트 윈도우 context window",
    "툴콜링": "함수 호출 function calling tool",
    "도구호출": "함수 호출 function calling tool",
    "에이전트간": "a2a agent to agent",
    "모델컨텍스트프로토콜": "mcp model context protocol",
    "검색기": "retriever retrieval",
    "재순위": "재정렬 reranking",
    "사설연결": "private endpoint vnet",
    "권한관리": "rbac iam",
    "모니터링": "관측 가능성 observability tracing logging",
    "gpu 메모리": "gpu vram",
    "쿠버": "kubernetes k8s 쿠버네티스",
    "케이에이트에스": "kubernetes k8s 쿠버네티스",
    "파드": "pod kubernetes 파드",
    "키볼트": "key vault azure 비밀 정보",
    "관리형아이디": "managed identity 관리형 id",
    "프롬프트캐시": "prompt caching 프롬프트 캐싱",
    "배치추론": "dynamic batching batch inference 동적 배칭",
    "코사인": "cosine similarity 코사인 유사도",
    "사람승인": "human in the loop 사람 검토 단계",
}


def normalize(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r"[^0-9a-z가-힣+.-]+", " ", text)


def _tokens(text: str) -> set[str]:
    normalized = normalize(text)
    tokens = {token for token in normalized.split() if len(token) > 1}
    # Pull Latin acronyms out of Korean particles (for example, "RAG가").
    tokens.update(re.findall(r"[a-z][a-z0-9+.-]+", normalized))
    for alias, expansion in ALIASES.items():
        if alias in normalized:
            tokens.update(normalize(expansion).split())
    return tokens


def term_text(term: Term) -> str:
    return " ".join(
        (
            term.name,
            term.english,
            term.category,
            term.summary,
            term.definition,
            term.infra,
            term.example,
            " ".join(term.related),
            " ".join(term.tags),
        )
    )


def search_terms(
    query: str,
    *,
    category: str | None = None,
    level: str | None = None,
    limit: int = 5,
) -> list[tuple[Term, float]]:
    """Return ranked cards using exact, alias and token-overlap signals."""
    query_norm = normalize(query)
    query_tokens = _tokens(query)
    results: list[tuple[Term, float]] = []

    for term in TERMS:
        if category and category != "전체" and term.category != category:
            continue
        if level and level != "전체" and term.level != level:
            continue

        haystack = normalize(term_text(term))
        haystack_tokens = _tokens(haystack)
        name_tokens = _tokens(term.name + " " + term.english)
        score = 0.0
        if query_norm:
            if query_norm == normalize(term.name) or query_norm == normalize(term.english):
                score += 20
            elif query_norm in normalize(term.name) or query_norm in normalize(term.english):
                score += 11
            if query_norm in haystack:
                score += 4
            score += 2.2 * len(query_tokens & haystack_tokens)
            # Exact token matches in the term name should outrank incidental
            # mentions inside definitions or related-term lists.
            score += 5 * len(query_tokens & name_tokens)
        else:
            score = 1

        # A single generic overlap such as "질문" is not enough to claim a hit.
        if score >= 3.5:
            results.append((term, score))

    results.sort(key=lambda item: (-item[1], LEVELS.index(item[0].level), item[0].name))
    return results[: max(1, limit)]


def filter_terms(category: str = "전체", level: str = "전체") -> list[Term]:
    return [
        term
        for term in TERMS
        if (category == "전체" or term.category == category)
        and (level == "전체" or term.level == level)
    ]


def related_terms(term: Term) -> list[Term]:
    related_names = set(term.related)
    return [candidate for candidate in TERMS if candidate.name in related_names]


def validate_catalog(terms: Iterable[Term] = TERMS) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    names: set[str] = set()
    for term in terms:
        if term.id in ids:
            errors.append(f"duplicate id: {term.id}")
        if term.name in names:
            errors.append(f"duplicate name: {term.name}")
        ids.add(term.id)
        names.add(term.name)
        for field_name in ("name", "summary", "definition", "analogy", "infra", "example"):
            if not getattr(term, field_name).strip():
                errors.append(f"{term.id}: empty {field_name}")
        if term.category not in CATEGORIES:
            errors.append(f"{term.id}: invalid category")
        if term.level not in LEVELS:
            errors.append(f"{term.id}: invalid level")
    return errors
