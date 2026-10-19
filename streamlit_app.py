from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime
from typing import Any

import streamlit as st

from src.knowledge import CATEGORIES, LEVELS, TERM_BY_ID, TERMS, Term, filter_terms, related_terms, search_terms
from src.quiz import build_question, recommended_terms, update_mastery
from src.tutor import MAX_QUERY_CHARS, ask_tutor


st.set_page_config(
    page_title="InfraMate · AI 인프라 튜터",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


PALETTE = {
    "LLM 핵심": "#7C3AED",
    "RAG·데이터": "#0EA5E9",
    "에이전트·작업 흐름": "#F97316",
    "클라우드·배포": "#10B981",
    "보안·운영": "#EF4444",
    "프로토콜": "#6366F1",
}

ROLE_PATHS = {
    "입문자": ["token", "context-window", "inference", "rag", "ai-agent", "azure-openai", "mcp"],
    "기획자·PM": ["hallucination", "rag", "ai-agent", "multi-agent", "observability", "guardrail", "a2a"],
    "개발자": ["structured-output", "function-calling", "retriever", "langgraph", "container", "secrets", "mcp"],
    "데이터·AI 담당자": ["embedding", "chunking", "vector-db", "hnsw", "reranking", "rag", "observability"],
    "인프라·운영 담당자": ["gpu", "deployment", "endpoint", "rate-limit", "autoscaling", "private-endpoint", "observability"],
}

TAG_LABELS = {
    "tokenizer": "토크나이저",
    "context": "문맥",
    "serving": "모델 제공",
    "latency": "응답 지연",
    "throughput": "처리량",
    "sampling": "샘플링",
    "json": "JSON",
    "schema": "스키마",
    "tool calling": "도구 호출",
    "api": "API",
    "vector": "벡터",
    "embedding model": "임베딩 모델",
    "grounding": "근거 기반 답변",
    "split": "문서 분할",
    "overlap": "겹침",
    "vector store": "벡터 저장소",
    "retrieval": "검색",
    "top-k": "상위 K개",
    "mmr": "MMR",
    "bm25": "BM25",
    "lexical": "키워드 검색",
    "semantic": "의미 검색",
    "rank": "순위",
    "cross encoder": "교차 인코더",
    "post retrieval": "검색 후 처리",
    "agent": "에이전트",
    "function": "함수",
    "workflow": "작업 흐름",
    "session": "세션",
    "framework": "프레임워크",
    "chain": "처리 흐름",
    "integration": "연동",
    "graph": "그래프",
    "node": "노드",
    "edge": "연결선",
    "role": "역할",
    "orchestration": "작업 조율",
    "aoai": "Azure OpenAI",
    "enterprise": "기업용",
    "model serving": "모델 제공",
    "capacity": "처리 용량",
    "url": "URL",
    "network": "네트워크",
    "version": "버전",
    "compatibility": "호환성",
    "preview": "미리 보기",
    "throttling": "요청 제한",
    "accelerator": "가속기",
    "cuda": "CUDA",
    "hardware": "하드웨어",
    "docker": "Docker",
    "image": "이미지",
    "runtime": "실행 환경",
    "scale": "자원 확장",
    "hpa": "HPA",
    "private link": "Private Link",
    "least privilege": "최소 권한",
    "api key": "API 키",
    "vault": "보안 저장소",
    "credential": "인증 정보",
    "jailbreak": "탈옥 공격",
    "security": "보안",
    "untrusted data": "신뢰할 수 없는 데이터",
    "model context protocol": "모델 컨텍스트 프로토콜",
    "host": "호스트",
    "client": "클라이언트",
    "server": "서버",
    "agent to agent": "에이전트 간 통신",
    "protocol": "프로토콜",
    "task": "작업",
}


def inject_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #132238;
            --muted: #5C6C80;
            --line: #DDE6F0;
            --brand: #5B5BD6;
            --brand2: #14B8A6;
            --soft: #F5F7FB;
        }
        .stApp { background: linear-gradient(180deg, #F7F9FD 0%, #FFFFFF 38%); color: var(--ink); }
        [data-testid="stSidebar"] { background: #111B2E; border-right: 1px solid #26344B; }
        [data-testid="stSidebar"] * { color: #EFF4FF; }
        [data-testid="stSidebar"] [data-baseweb="select"] * { color: #111B2E; }
        [data-testid="stSidebar"] .stRadio label { background: transparent; padding: .32rem .35rem; border-radius: .6rem; }
        [data-testid="stSidebar"] hr { border-color: #2B3950; }
        .block-container { max-width: 1220px; padding-top: 2.1rem; padding-bottom: 4rem; }
        h1, h2, h3 { letter-spacing: -0.035em; color: var(--ink); }
        .hero {
            padding: 2.1rem 2.25rem; border-radius: 24px;
            background: radial-gradient(circle at 85% 12%, rgba(45,212,191,.34), transparent 31%),
                        linear-gradient(135deg, #18233D 0%, #283969 58%, #4C51BF 100%);
            color: white; box-shadow: 0 18px 55px rgba(29,42,78,.19); margin-bottom: 1.4rem;
        }
        .hero .eyebrow { font-size: .78rem; font-weight: 750; letter-spacing: .13em; color: #8FF6E7; }
        .hero h1 { color: white; font-size: clamp(2rem, 4vw, 3.5rem); margin: .35rem 0 .6rem; line-height: 1.06; }
        .hero p { color: #DCE6FB; font-size: 1.04rem; max-width: 760px; margin: 0; line-height: 1.65; }
        .metric-card, .term-card, .info-card {
            background: rgba(255,255,255,.92); border: 1px solid var(--line); border-radius: 18px;
            padding: 1.15rem 1.2rem; box-shadow: 0 8px 28px rgba(33,51,84,.06); height: 100%;
        }
        .metric-label { color: var(--muted); font-size: .8rem; font-weight: 700; }
        .metric-value { color: var(--ink); font-size: 1.75rem; font-weight: 850; margin: .1rem 0; }
        .metric-note { color: #748297; font-size: .76rem; }
        .term-kicker { text-transform: uppercase; letter-spacing: .08em; font-size: .7rem; font-weight: 800; }
        .term-name { font-size: 1.2rem; font-weight: 850; color: var(--ink); margin: .3rem 0 .4rem; word-break: keep-all; }
        .term-card .term-name { font-size: 1.05rem; overflow-wrap: normal; }
        .term-summary { color: var(--muted); line-height: 1.55; font-size: .9rem; }
        .pill { display: inline-block; border: 1px solid #D7E0EE; background: #F7F9FD; color: #506078;
                border-radius: 999px; padding: .22rem .62rem; margin: .12rem .25rem .12rem 0; font-size: .74rem; font-weight: 650; }
        .mode { display:inline-flex; align-items:center; gap:.35rem; border-radius:999px; padding:.3rem .7rem;
                background:#E9FBF7; color:#087B69; border:1px solid #B7EEE3; font-size:.77rem; font-weight:750; }
        .mode:before { content:''; width:.48rem; height:.48rem; border-radius:50%; background:#14B8A6; }
        .flow { display:flex; flex-wrap:wrap; align-items:center; gap:.45rem; margin:.8rem 0 1.35rem; }
        .flow-step { padding:.7rem .9rem; background:white; border:1px solid #D9E2EE; border-radius:12px;
                     font-size:.82rem; font-weight:750; color:#2C3B53; box-shadow:0 5px 16px rgba(33,51,84,.05); }
        .flow-arrow { color:#94A3B8; font-weight:900; }
        .source-box { border-left: 3px solid #64748B; background:#F8FAFC; padding:.75rem .95rem; border-radius:0 10px 10px 0; color:#526175; font-size:.82rem; }
        div[data-testid="stMetric"] { background: white; border: 1px solid var(--line); padding: 1rem; border-radius: 16px; }
        div[data-testid="stChatMessage"] { border: 1px solid #E2E8F0; background: rgba(255,255,255,.82); border-radius: 16px; padding: .2rem .4rem; }
        .stButton > button { border-radius: 11px; font-weight: 720; border: 1px solid #CCD7E5; }
        .stButton > button[kind="primary"] { background: linear-gradient(135deg,#5B5BD6,#4F46E5); border: 0; }
        @media (max-width: 700px) { .hero { padding:1.5rem; border-radius:18px; } .block-container {padding-top:1rem;} }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults: dict[str, Any] = {
        "profile": {"name": "학습자", "role": "입문자", "level": "입문", "interests": ["LLM 핵심", "RAG·데이터"]},
        "learned": [],
        "mastery": {},
        "review_queue": [],
        "history": [],
        "chat_messages": [
            {
                "role": "assistant",
                "content": "안녕하세요! 어려운 AI 인프라 용어를 쉬운 비유와 실무 사례로 설명해 드릴게요. `RAG가 뭐야?`처럼 질문해 보세요.",
                "mode": "기본 학습 모드",
                "cards": [],
            }
        ],
        "quiz_ids": [],
        "quiz_pos": 0,
        "quiz_score": 0,
        "quiz_feedback": None,
        "quiz_seed": 0,
        "selected_term": "rag",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def config() -> dict[str, Any]:
    keys = (
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_OPENAI_API_VERSION",
    )
    values = {key: os.getenv(key, "") for key in keys}
    try:
        for key in keys:
            if not values[key] and key in st.secrets:
                values[key] = st.secrets[key]
    except Exception:
        pass
    return values


def active_mode() -> str:
    settings = config()
    if all(settings.get(k) for k in ("AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT")):
        return "AI 답변 모드 · Azure OpenAI"
    if settings.get("OPENAI_API_KEY"):
        return "AI 답변 모드 · OpenAI"
    return "기본 학습 모드"


def metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def term_card(term: Term) -> None:
    color = PALETTE.get(term.category, "#5B5BD6")
    st.markdown(
        f"""
        <div class="term-card">
          <div class="term-kicker" style="color:{color}">{term.category} · {term.level}</div>
          <div class="term-name">{term.name}</div>
          <div class="term-summary">{term.summary}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mark_learned(term: Term) -> None:
    if term.id not in st.session_state.learned:
        st.session_state.learned.append(term.id)
    st.session_state.mastery[term.id] = max(st.session_state.mastery.get(term.id, 0.0), 0.25)
    st.session_state.history.append(
        {"time": datetime.now().isoformat(timespec="seconds"), "type": "lesson", "term": term.name, "result": "학습 완료"}
    )


def sidebar() -> str:
    with st.sidebar:
        st.markdown("## 🧭 InfraMate")
        st.caption("AI 인프라 용어 학습 튜터")
        st.markdown(f'<span class="mode">{active_mode()}</span>', unsafe_allow_html=True)
        st.markdown("---")
        page = st.radio(
            "메뉴",
            ("대시보드", "용어 학습", "AI 튜터", "퀴즈", "학습 기록", "서비스 구조"),
            label_visibility="collapsed",
        )
        st.markdown("---")
        with st.expander("내 학습 설정", expanded=False):
            profile = st.session_state.profile
            with st.form("profile_form"):
                name = st.text_input("이름", profile["name"], max_chars=20)
                role = st.selectbox("역할", tuple(ROLE_PATHS), index=tuple(ROLE_PATHS).index(profile["role"]))
                level = st.selectbox("설명 난이도", LEVELS, index=LEVELS.index(profile["level"]))
                interests = st.multiselect("관심 영역", CATEGORIES, default=profile["interests"])
                if st.form_submit_button("설정 저장", use_container_width=True):
                    st.session_state.profile = {
                        "name": name.strip() or "학습자",
                        "role": role,
                        "level": level,
                        "interests": interests,
                    }
                    st.success("저장했습니다.")
        st.caption("강의 내용을 바탕으로 다시 구성한 교육용 시제품")
        return page


def dashboard() -> None:
    profile = st.session_state.profile
    learned_count = len(st.session_state.learned)
    mastery_values = list(st.session_state.mastery.values())
    average = round(sum(mastery_values) / len(mastery_values) * 100) if mastery_values else 0
    quiz_events = [item for item in st.session_state.history if item["type"] == "quiz"]
    correct = sum(1 for item in quiz_events if item["result"] == "정답")
    accuracy = round(correct / len(quiz_events) * 100) if quiz_events else 0

    st.markdown(
        f"""
        <div class="hero">
          <div class="eyebrow">AI 인프라 맞춤 학습 튜터</div>
          <h1>낯선 인프라 용어를<br/>내 업무의 언어로.</h1>
          <p>{profile['name']}님의 역할과 학습 수준에 맞춰 핵심 개념을 설명하고, 퀴즈 결과를 바탕으로 헷갈린 개념과 다음 학습 내용을 추천합니다.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    with cols[0]:
        metric_card("학습한 용어", f"{learned_count}개", f"전체 {len(TERMS)}개 중")
    with cols[1]:
        metric_card("평균 숙련도", f"{average}%", "퀴즈 결과로 계산")
    with cols[2]:
        metric_card("퀴즈 정답률", f"{accuracy}%", f"누적 {len(quiz_events)}문항")
    with cols[3]:
        metric_card("복습할 용어", f"{len(st.session_state.review_queue)}개", "틀리거나 헷갈린 개념")

    st.markdown("### 오늘 배울 용어")
    recommendations = recommended_terms(
        st.session_state.mastery,
        st.session_state.learned,
        interests=profile["interests"],
        limit=3,
    )
    columns = st.columns(3)
    for column, term in zip(columns, recommendations):
        with column:
            term_card(term)
            if st.button("이 용어 배우기", key=f"dash_{term.id}", use_container_width=True):
                st.session_state.selected_term = term.id
                st.info("왼쪽 메뉴에서 ‘용어 학습’을 선택하면 이 용어를 바로 볼 수 있어요.")

    st.markdown("### 추천 학습 순서")
    path = [TERM_BY_ID[item] for item in ROLE_PATHS[profile["role"]]]
    flow = []
    for index, term in enumerate(path):
        status = "✓ " if term.id in st.session_state.learned else ""
        flow.append(f'<span class="flow-step">{status}{term.name}</span>')
        if index < len(path) - 1:
            flow.append('<span class="flow-arrow">→</span>')
    st.markdown(f'<div class="flow">{"".join(flow)}</div>', unsafe_allow_html=True)

    with st.expander("이 튜터는 어떻게 학습을 돕나요?"):
        st.markdown(
            """
            1. **관련 지식 찾기** — 질문에서 핵심 용어와 연관 개념을 찾습니다.
            2. **수준별 설명** — 학습자의 수준과 직무에 맞춰 설명합니다.
            3. **이해도 확인** — 정의·비교·상황형 퀴즈로 이해도를 확인합니다.
            4. **맞춤 복습** — 오답과 낮은 확신도를 복습 목록에 반영합니다.
            """
        )


def learn_page() -> None:
    st.title("용어 학습")
    st.caption("검색어와 분야, 난이도를 선택해 한 번에 하나의 개념을 익혀보세요.")

    filter_cols = st.columns((2.2, 1, 1))
    with filter_cols[0]:
        query = st.text_input("용어 검색", placeholder="예: RAG, GPU 메모리, 도구 호출", max_chars=80)
    with filter_cols[1]:
        category = st.selectbox("영역", ("전체", *CATEGORIES))
    with filter_cols[2]:
        level = st.selectbox("난이도", ("전체", *LEVELS))

    if query.strip():
        candidates = [term for term, _score in search_terms(query, category=category, level=level, limit=50)]
    else:
        candidates = filter_terms(category, level)
    if not candidates:
        st.warning("조건에 맞는 용어가 없습니다. 검색어나 필터를 바꿔보세요.")
        return

    candidate_ids = [term.id for term in candidates]
    selected_default = st.session_state.selected_term if st.session_state.selected_term in candidate_ids else candidate_ids[0]
    selected_id = st.selectbox(
        "학습할 용어",
        candidate_ids,
        index=candidate_ids.index(selected_default),
        format_func=lambda item: f"{TERM_BY_ID[item].name} · {TERM_BY_ID[item].english}",
    )
    st.session_state.selected_term = selected_id
    term = TERM_BY_ID[selected_id]

    color = PALETTE.get(term.category, "#5B5BD6")
    st.markdown(
        f"""
        <div class="hero" style="background:linear-gradient(135deg,#172238 0%,{color} 145%);padding:1.65rem 1.9rem">
          <div class="eyebrow">{term.category.upper()} · {term.level}</div>
          <h1 style="font-size:2.45rem">{term.name}</h1>
          <p>{term.english}<br/><strong style="color:white">{term.summary}</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_core, tab_infra, tab_links, tab_source = st.tabs(("핵심 이해", "인프라 관점", "함께 알아둘 용어", "학습 출처"))
    with tab_core:
        left, right = st.columns(2)
        with left:
            st.markdown("#### 핵심 정의")
            st.write(term.definition)
        with right:
            st.markdown("#### 쉬운 비유")
            st.info(term.analogy, icon="💡")
    with tab_infra:
        st.markdown("#### 인프라 업무에서 왜 중요할까요?")
        st.write(term.infra)
        st.markdown("#### 실무 활용 예시")
        st.success(term.example, icon="🛠️")
    with tab_links:
        linked = related_terms(term)
        if linked:
            cols = st.columns(min(3, len(linked)))
            for index, linked_term in enumerate(linked):
                with cols[index % len(cols)]:
                    term_card(linked_term)
        else:
            st.write("아직 연결된 용어가 없습니다.")
        st.markdown(
            " ".join(f'<span class="pill">#{TAG_LABELS.get(tag.lower(), tag)}</span>' for tag in term.tags),
            unsafe_allow_html=True,
        )
    with tab_source:
        st.markdown(
            f'<div class="source-box">학습 영역: <strong>{term.source}</strong><br/>공식 문서를 바탕으로 학습하기 쉽게 다시 작성한 설명입니다.</div>',
            unsafe_allow_html=True,
        )
        if term.reference_url:
            st.link_button("공식 문서에서 더 알아보기", term.reference_url, use_container_width=True)

    progress = st.session_state.mastery.get(term.id, 0.0)
    st.progress(progress, text=f"현재 숙련도 {round(progress * 100)}%")
    action_cols = st.columns((1, 1, 2))
    with action_cols[0]:
        if st.button("✓ 학습 완료", type="primary", use_container_width=True):
            mark_learned(term)
            st.toast(f"{term.name} 학습을 기록했습니다.")
            st.rerun()
    with action_cols[1]:
        if st.button("이 용어 퀴즈 풀기", use_container_width=True):
            st.session_state.quiz_ids = [term.id]
            st.session_state.quiz_pos = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_feedback = None
            st.info("왼쪽 메뉴에서 ‘퀴즈’를 선택하세요.")


def submit_chat(question: str) -> None:
    question = question.strip()
    if not question:
        return
    st.session_state.chat_messages.append({"role": "user", "content": question})
    reply = ask_tutor(
        question,
        config(),
        level=st.session_state.profile["level"],
        role=st.session_state.profile["role"],
    )
    st.session_state.chat_messages.append(
        {
            "role": "assistant",
            "content": reply.text,
            "mode": reply.mode,
            "notice": reply.notice,
            "cards": [term.id for term in reply.cards],
        }
    )


def tutor_page() -> None:
    st.title("AI 튜터")
    st.caption("API 키가 없어도 기본 설명 기능을 사용할 수 있습니다. 배포 환경에 API 키를 등록하면 생성형 AI 답변 기능이 켜집니다.")
    st.markdown(f'<span class="mode">{active_mode()}</span>', unsafe_allow_html=True)

    st.markdown("#### 이렇게 물어보세요")
    quick_cols = st.columns(4)
    prompts = ("RAG가 뭐야?", "MCP와 A2A의 차이는?", "GPU가 왜 필요해?", "프라이빗 엔드포인트가 뭐야?")
    for col, prompt in zip(quick_cols, prompts):
        with col:
            if st.button(prompt, key=f"quick_{prompt}", use_container_width=True):
                submit_chat(prompt)
                st.rerun()

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("mode"):
                st.caption(message["mode"])
                if message.get("notice"):
                    st.info(message["notice"])
                if message.get("cards"):
                    with st.expander("답변에 참고한 용어"):
                        for term_id in message["cards"]:
                            term = TERM_BY_ID[term_id]
                            st.markdown(f"- **{term.name}** — {term.summary}")

    question = st.chat_input("궁금한 AI 인프라 용어를 물어보세요", max_chars=MAX_QUERY_CHARS)
    if question:
        submit_chat(question)
        st.rerun()


def start_quiz(term_ids: list[str] | None = None) -> None:
    if term_ids is None:
        terms = recommended_terms(
            st.session_state.mastery,
            st.session_state.learned,
            interests=st.session_state.profile["interests"],
            limit=5,
        )
        term_ids = [term.id for term in terms]
    st.session_state.quiz_ids = term_ids
    st.session_state.quiz_pos = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_feedback = None
    st.session_state.quiz_seed += 1


def quiz_page() -> None:
    st.title("맞춤형 퀴즈")
    st.caption("답이 맞았는지와 얼마나 확신했는지를 바탕으로 다음 복습 내용을 추천합니다.")

    if not st.session_state.quiz_ids:
        st.markdown(
            """
            <div class="info-card">
              <div class="term-kicker" style="color:#5B5BD6">맞춤형 이해도 점검</div>
              <div class="term-name">오늘의 맞춤 퀴즈 5문항</div>
              <div class="term-summary">관심 분야와 현재 숙련도에 맞춰 문제를 고릅니다. API 키가 없어도 이용할 수 있습니다.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("퀴즈 시작", type="primary", use_container_width=True):
            start_quiz()
            st.rerun()
        return

    position = st.session_state.quiz_pos
    total = len(st.session_state.quiz_ids)
    if position >= total:
        score = st.session_state.quiz_score
        st.success(f"퀴즈 완료! {total}문항 중 {score}문항을 맞혔습니다.", icon="🎉")
        weak = [TERM_BY_ID[term_id].name for term_id in st.session_state.review_queue[-3:]]
        if weak:
            st.info(f"복습하면 좋은 용어: {', '.join(weak)}")
        if st.button("새 퀴즈 풀기", type="primary"):
            start_quiz()
            st.rerun()
        return

    term = TERM_BY_ID[st.session_state.quiz_ids[position]]
    question = build_question(term, seed=st.session_state.quiz_seed)
    st.progress(position / total, text=f"{position + 1} / {total}")

    st.markdown(f"### Q{position + 1}. {question.prompt}")
    feedback = st.session_state.quiz_feedback
    if feedback is None:
        with st.form(f"quiz_form_{position}_{term.id}"):
            answer = st.radio("답을 선택하세요", question.options, index=None)
            confidence = st.radio("이 답에 얼마나 확신하나요?", ("확신해요", "조금 헷갈려요"), horizontal=True)
            submitted = st.form_submit_button("정답 확인", type="primary", use_container_width=True)
        if submitted:
            if answer is None:
                st.warning("답을 하나 선택해 주세요.")
            else:
                correct = answer == question.answer
                current = st.session_state.mastery.get(term.id, 0.0)
                st.session_state.mastery[term.id] = update_mastery(current, correct, confidence)
                if term.id not in st.session_state.learned:
                    st.session_state.learned.append(term.id)
                if correct:
                    st.session_state.quiz_score += 1
                    if term.id in st.session_state.review_queue and confidence == "확신해요":
                        st.session_state.review_queue.remove(term.id)
                elif term.id not in st.session_state.review_queue:
                    st.session_state.review_queue.append(term.id)
                st.session_state.history.append(
                    {
                        "time": datetime.now().isoformat(timespec="seconds"),
                        "type": "quiz",
                        "term": term.name,
                        "result": "정답" if correct else "오답",
                        "confidence": confidence,
                    }
                )
                st.session_state.quiz_feedback = {"correct": correct, "answer": answer}
                st.rerun()
    else:
        if feedback["correct"]:
            st.success("정답입니다!", icon="✅")
        else:
            st.error(f"선택한 답: {feedback['answer']} · 정답: {question.answer}", icon="🧩")
        st.markdown(f"**해설**  \n{question.explanation}")
        if not feedback["correct"]:
            st.info(f"헷갈린 개념 다시 보기: **{term.name}** — {term.analogy}")
        if st.button("다음 문항", type="primary", use_container_width=True):
            st.session_state.quiz_pos += 1
            st.session_state.quiz_feedback = None
            st.rerun()


def history_page() -> None:
    st.title("학습 기록")
    st.caption("현재 접속 중에 쌓인 학습 기록입니다. 다음 접속 때도 이어서 보려면 외부 데이터베이스를 연결해야 합니다.")

    mastered = sum(1 for value in st.session_state.mastery.values() if value >= 0.8)
    reviewing = len(st.session_state.review_queue)
    cols = st.columns(3)
    cols[0].metric("학습 완료", f"{len(st.session_state.learned)}개")
    cols[1].metric("익숙해진 용어", f"{mastered}개", help="숙련도 80% 이상")
    cols[2].metric("복습할 용어", f"{reviewing}개")

    st.markdown("### 영역별 진도")
    learned_categories = Counter(TERM_BY_ID[item].category for item in st.session_state.learned)
    total_categories = Counter(term.category for term in TERMS)
    chart = {
        category: round(learned_categories[category] / total_categories[category] * 100)
        for category in CATEGORIES
    }
    st.bar_chart(chart, horizontal=True, x_label="학습 진도(%)", y_label="분야")

    if st.session_state.review_queue:
        st.markdown("### 복습할 용어")
        columns = st.columns(min(3, len(st.session_state.review_queue)))
        for index, term_id in enumerate(st.session_state.review_queue):
            with columns[index % len(columns)]:
                term_card(TERM_BY_ID[term_id])

    st.markdown("### 최근 활동")
    if st.session_state.history:
        for item in reversed(st.session_state.history[-10:]):
            icon = "✅" if item["result"] in ("정답", "학습 완료") else "🧩"
            st.write(f"{icon} **{item['term']}** · {item['result']} · {item['time'].replace('T', ' ')}")
    else:
        st.info("아직 학습 기록이 없습니다.")

    export = {
        "profile": st.session_state.profile,
        "learned": st.session_state.learned,
        "mastery": st.session_state.mastery,
        "review_queue": st.session_state.review_queue,
        "history": st.session_state.history,
        "exported_at": datetime.now().isoformat(timespec="seconds"),
    }
    st.download_button(
        "학습 기록 내려받기 (JSON)",
        data=json.dumps(export, ensure_ascii=False, indent=2),
        file_name="inframate_learning_progress.json",
        mime="application/json",
    )


def architecture_page() -> None:
    st.title("서비스 구조")
    st.caption("강의에서 다룬 LLM, RAG, 에이전트, 서비스 배포, MCP·A2A를 하나의 학습 흐름으로 연결했습니다.")

    st.markdown("### 학습 흐름")
    st.markdown(
        """
        <div class="flow">
          <span class="flow-step">① 역할과 학습 수준 설정</span><span class="flow-arrow">→</span>
          <span class="flow-step">② 관련 용어 찾기</span><span class="flow-arrow">→</span>
          <span class="flow-step">③ 맞춤 설명</span><span class="flow-arrow">→</span>
          <span class="flow-step">④ 퀴즈로 이해도 확인</span><span class="flow-arrow">→</span>
          <span class="flow-step">⑤ 헷갈린 개념 복습</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 서비스 구성")
    layers = st.columns(4)
    cards = (
        ("01 · 학습 화면", "Streamlit 화면", "용어 카드, 대화형 질문, 퀴즈, 학습 현황"),
        ("02 · 학습 흐름", "학습 튜터", "검색 → 설명 → 평가 → 다음 학습 추천"),
        ("03 · 지식 검색", "앱에 담긴 용어 자료", "직접 작성한 용어 카드, 동의어, 관련도 순위"),
        ("04 · 답변 생성", "기본 모드 / OpenAI / Azure", "키 없이 작동하며 필요할 때 생성형 AI를 연결"),
    )
    for column, (eyebrow, title, body) in zip(layers, cards):
        with column:
            st.markdown(
                f'<div class="info-card"><div class="term-kicker" style="color:#5B5BD6">{eyebrow}</div><div class="term-name">{title}</div><div class="term-summary">{body}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("### 실제 운영을 위한 준비 사항")
    left, right = st.columns(2)
    with left:
        st.markdown(
            """
            **현재 구현된 기능**
            - API 키 없이 동작하는 용어 검색과 설명
            - 접속 중에 유지되는 학습 기록
            - OpenAI 또는 Azure OpenAI 설정 자동 인식
            - 생성형 AI 연결 오류 시 기본 학습 모드로 자동 전환
            - 원본 강의 자료 대신 새로 작성한 용어 카드 제공
            """
        )
    with right:
        st.markdown(
            """
            **정식 운영 시 추가할 기능**
            - LangGraph 기반 상태 관리와 조건별 흐름 제어
            - 사내 문서 권한을 그대로 따르는 검색 증강 생성(RAG)
            - Entra ID·RBAC 인증과 프라이빗 엔드포인트
            - 외부 데이터베이스를 통한 사용자별 학습 기록 보관
            - 실행 경로 추적, 품질 평가, 비용·응답 시간 모니터링
            """
        )

    with st.expander("생성형 AI 연결 설정 예시"):
        st.code(
            """# .streamlit/secrets.toml 또는 Streamlit Cloud의 비밀 값 설정
# OpenAI
OPENAI_API_KEY = "..."
OPENAI_MODEL = "gpt-4.1-mini"

# 또는 Azure OpenAI
AZURE_OPENAI_API_KEY = "..."
AZURE_OPENAI_ENDPOINT = "https://<resource>.openai.azure.com"
AZURE_OPENAI_DEPLOYMENT = "<deployment-name>"
AZURE_OPENAI_API_VERSION = "<supported-api-version>"
""",
            language="toml",
        )


inject_style()
init_state()
selected_page = sidebar()

PAGES = {
    "대시보드": dashboard,
    "용어 학습": learn_page,
    "AI 튜터": tutor_page,
    "퀴즈": quiz_page,
    "학습 기록": history_page,
    "서비스 구조": architecture_page,
}
PAGES[selected_page]()

