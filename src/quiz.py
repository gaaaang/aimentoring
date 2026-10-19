"""Deterministic quiz generation and mastery updates."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .knowledge import LEVELS, TERMS, Term


@dataclass(frozen=True)
class QuizQuestion:
    term_id: str
    prompt: str
    options: tuple[str, ...]
    answer: str
    explanation: str


def build_question(term: Term, seed: int = 0) -> QuizQuestion:
    pool = [candidate.name for candidate in TERMS if candidate.id != term.id and candidate.category != term.category]
    rng = random.Random(f"{term.id}:{seed}")
    distractors = rng.sample(pool, k=min(3, len(pool)))
    options = [term.name, *distractors]
    rng.shuffle(options)
    return QuizQuestion(
        term_id=term.id,
        prompt=f"다음 설명과 가장 잘 맞는 용어는 무엇일까요?\n\n{term.summary}",
        options=tuple(options),
        answer=term.name,
        explanation=f"정답은 ‘{term.name}’입니다.\n\n{term.definition}\n\n{term.infra}",
    )


def update_mastery(current: float, correct: bool, confidence: str) -> float:
    if correct:
        gain = 0.22 if confidence == "확신해요" else 0.14
        return min(1.0, round(current + gain, 2))
    loss = 0.13 if confidence == "확신해요" else 0.07
    return max(0.0, round(current - loss, 2))


def recommended_terms(
    mastery: dict[str, float],
    learned: list[str],
    *,
    interests: list[str] | None = None,
    limit: int = 5,
) -> list[Term]:
    interests = interests or []
    learned_set = set(learned)

    def priority(term: Term) -> tuple[float, int, str]:
        score = mastery.get(term.id, 0.0)
        if term.id not in learned_set:
            score -= 0.15
        if term.category in interests:
            score -= 0.25
        return (score, LEVELS.index(term.level), term.name)

    return sorted(TERMS, key=priority)[:limit]


def diagnostic_questions() -> tuple[QuizQuestion, ...]:
    lookup = {term.id: term for term in TERMS}
    return tuple(
        build_question(lookup[term_id], seed=index + 11)
        for index, term_id in enumerate(("token", "rag", "langgraph", "private-endpoint", "mcp"))
    )
