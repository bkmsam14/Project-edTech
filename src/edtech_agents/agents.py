from __future__ import annotations

import re
from collections import defaultdict
from difflib import SequenceMatcher
from typing import DefaultDict


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "how",
    "if",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "uses",
    "using",
    "was",
    "what",
    "when",
    "which",
    "with",
    "you",
    "your",
}


_STUDENT_TOPIC_HISTORY: DefaultDict[str, DefaultDict[str, dict]] = defaultdict(
    lambda: defaultdict(lambda: {"attempts": 0, "incorrect": 0, "hints_used": 0})
)


def tutor_agent(
    student_id: str,
    question: str,
    lesson_chunks: list[str],
    dyslexia_mode: bool = True,
    hints_used: int = 0,
) -> dict:
    hints = generate_step_by_step_hints(
        lesson_chunks=lesson_chunks,
        question=question,
        dyslexia_mode=dyslexia_mode,
        hints_used=hints_used,
    )
    quiz = generate_quiz(lesson_chunks=lesson_chunks, question=question)

    return {
        "student_id": student_id,
        "question": question,
        "hints": hints,
        "quiz": quiz,
        "dyslexia_mode": dyslexia_mode,
    }


def generate_step_by_step_hints(
    lesson_chunks: list[str],
    question: str = "",
    dyslexia_mode: bool = True,
    hints_used: int = 0,
) -> list[dict]:
    sentences = _extract_sentences(lesson_chunks)
    if not sentences:
        return []

    ranked_sentences = _rank_sentences(sentences, question)
    support_level = _support_level(hints_used)
    max_hints = 2 if hints_used <= 0 else 3 if hints_used == 1 else 4

    hints: list[dict] = []
    keywords = _extract_keywords(" ".join(ranked_sentences[:2]))[:3]
    if keywords:
        focus_text = f"Focus on these key terms: {', '.join(keywords)}."
    else:
        focus_text = "Focus on the main idea in the lesson."

    hints.append(
        _hint_payload(
            level=1,
            text=focus_text,
            dyslexia_mode=dyslexia_mode,
            support_level=support_level,
        )
    )

    for index, sentence in enumerate(ranked_sentences[: max_hints - 1], start=2):
        prefix = "Start here:" if index == 2 else "Next step:"
        hints.append(
            _hint_payload(
                level=index,
                text=f"{prefix} {sentence}",
                dyslexia_mode=dyslexia_mode,
                support_level=support_level,
            )
        )

    if hints_used >= 2 and ranked_sentences:
        direct_clue = _build_direct_clue(ranked_sentences[0])
        hints.append(
            _hint_payload(
                level=len(hints) + 1,
                text=direct_clue,
                dyslexia_mode=dyslexia_mode,
                support_level=support_level,
            )
        )

    return hints[:max_hints]


def generate_quiz(
    lesson_chunks: list[str],
    question: str = "",
    max_questions: int = 3,
) -> list[dict]:
    sentences = _rank_sentences(_extract_sentences(lesson_chunks), question)
    all_keywords = _extract_keywords(" ".join(lesson_chunks))
    quiz: list[dict] = []

    for sentence in sentences:
        question_payload = _build_question_from_sentence(sentence, all_keywords)
        if question_payload:
            quiz.append(question_payload)
        if len(quiz) >= max(1, min(max_questions, 3)):
            break

    return quiz


def simplify_for_dyslexia(text: str) -> str:
    cleaned = _normalize_spacing(text)
    cleaned = re.sub(r"\s*[:;]\s*", ". ", cleaned)
    cleaned = re.sub(r"\((.*?)\)", r". \1.", cleaned)
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned) if part.strip()]

    simplified_parts = []
    for part in parts:
        words = part.split()
        if len(words) > 14:
            part = " ".join(words[:14]).rstrip(",") + "."
        simplified_parts.append(part)

    simplified = " ".join(simplified_parts).strip()
    highlighted = _highlight_keywords(simplified)
    return highlighted


def assessment_agent(
    student_id: str,
    question_id: str,
    student_answer: str,
    correct_answer: str,
    hints_used: int,
    topic: str,
) -> dict:
    answer_similarity = _answer_similarity(student_answer, correct_answer)
    is_correct = answer_similarity >= 0.86
    weakness_score = _compute_weakness_score(is_correct, hints_used, answer_similarity)
    _update_topic_history(student_id, topic, is_correct, hints_used)

    recommendation = _build_recommendation(
        is_correct=is_correct,
        weakness_score=weakness_score,
        hints_used=hints_used,
        topic=topic,
    )

    return {
        "student_id": student_id,
        "question_id": question_id,
        "is_correct": is_correct,
        "weakness_score": weakness_score,
        "recommendation": recommendation,
    }


def get_student_topic_summary(student_id: str) -> dict:
    topic_history = _STUDENT_TOPIC_HISTORY.get(student_id, {})
    summary = {}
    for topic, stats in topic_history.items():
        attempts = max(stats["attempts"], 1)
        summary[topic] = {
            "attempts": stats["attempts"],
            "incorrect": stats["incorrect"],
            "hints_used": stats["hints_used"],
            "mastery_score": round(1 - ((stats["incorrect"] * 2 + stats["hints_used"]) / (attempts * 4)), 2),
        }
    return summary


def reset_student_topic_history(student_id: str | None = None) -> None:
    if student_id is None:
        _STUDENT_TOPIC_HISTORY.clear()
        return
    _STUDENT_TOPIC_HISTORY.pop(student_id, None)


def _extract_sentences(lesson_chunks: list[str]) -> list[str]:
    sentences: list[str] = []
    for chunk in lesson_chunks:
        cleaned_chunk = _normalize_spacing(chunk)
        parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned_chunk) if part.strip()]
        for part in parts:
            stripped = part.strip(" .")
            if len(stripped.split()) >= 4:
                sentences.append(stripped + ("" if stripped.endswith((".", "!", "?")) else "."))
    return _dedupe(sentences)


def _rank_sentences(sentences: list[str], question: str) -> list[str]:
    if not question.strip():
        return sentences

    question_terms = set(_extract_keywords(question.lower()))
    scored = []
    for sentence in sentences:
        sentence_terms = set(_extract_keywords(sentence.lower()))
        overlap = len(question_terms & sentence_terms)
        scored.append((overlap, -len(sentence), sentence))
    scored.sort(reverse=True)
    return [sentence for _, _, sentence in scored]


def _extract_keywords(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z-]{2,}", text)
    seen = set()
    keywords = []
    for word in words:
        lowered = word.lower()
        if lowered in STOPWORDS:
            continue
        if lowered in seen:
            continue
        seen.add(lowered)
        keywords.append(word)
    return keywords


def _hint_payload(level: int, text: str, dyslexia_mode: bool, support_level: str) -> dict:
    display_text = simplify_for_dyslexia(text) if dyslexia_mode else _normalize_spacing(text)
    tts_text = re.sub(r"\*\*", "", display_text)
    return {
        "level": level,
        "support_level": support_level,
        "text": display_text,
        "tts_text": tts_text,
    }


def _support_level(hints_used: int) -> str:
    if hints_used <= 0:
        return "light"
    if hints_used == 1:
        return "guided"
    return "direct"


def _build_direct_clue(sentence: str) -> str:
    keywords = _extract_keywords(sentence)
    if keywords:
        return f"Direct clue: the answer is linked to {keywords[0]}. Read the sentence again."
    return f"Direct clue: read this idea again. {sentence}"


def _build_question_from_sentence(sentence: str, all_keywords: list[str]) -> dict | None:
    keywords = _extract_keywords(sentence)
    if not keywords:
        return None

    answer = keywords[0]
    answer_pattern = re.compile(rf"\b{re.escape(answer)}\b", re.IGNORECASE)
    prompt_text = answer_pattern.sub("____", sentence, count=1)
    prompt_text = prompt_text if prompt_text != sentence else f"Which key term completes this idea: {sentence}"

    distractors = [keyword for keyword in all_keywords if keyword.lower() != answer.lower()]
    distractors = _dedupe(distractors)[:3]

    if len(distractors) >= 3:
        options = _stable_options([answer, distractors[0], distractors[1], distractors[2]])
        return {
            "type": "multiple_choice",
            "question": prompt_text,
            "options": options,
            "correct_answer": answer,
        }

    return {
        "type": "short_answer",
        "question": f"In one short phrase, what key idea appears in this sentence: {sentence}",
        "correct_answer": answer,
    }


def _stable_options(options: list[str]) -> list[str]:
    return sorted(options, key=lambda item: (len(item), item.lower()))


def _answer_similarity(student_answer: str, correct_answer: str) -> float:
    normalized_student = _normalize_answer(student_answer)
    normalized_correct = _normalize_answer(correct_answer)

    if not normalized_student or not normalized_correct:
        return 0.0

    if normalized_student == normalized_correct:
        return 1.0

    student_tokens = set(normalized_student.split())
    correct_tokens = set(normalized_correct.split())
    overlap_score = len(student_tokens & correct_tokens) / max(len(correct_tokens), 1)
    sequence_score = SequenceMatcher(None, normalized_student, normalized_correct).ratio()
    return round(max(overlap_score, sequence_score), 3)


def _compute_weakness_score(is_correct: bool, hints_used: int, answer_similarity: float) -> float:
    incorrect_penalty = 0.0 if is_correct else 0.6
    hint_penalty = min(hints_used, 4) * 0.1
    confidence_penalty = max(0.0, 0.4 - (answer_similarity * 0.4))
    return round(min(1.0, incorrect_penalty + hint_penalty + confidence_penalty), 2)


def _build_recommendation(is_correct: bool, weakness_score: float, hints_used: int, topic: str) -> dict:
    if not is_correct and weakness_score >= 0.7:
        return {
            "next_action": "easier_explanation",
            "topic": topic,
            "message": "Review the same topic with a simpler explanation and one more guided hint.",
        }
    if not is_correct:
        return {
            "next_action": "show_hint",
            "topic": topic,
            "message": "Give one more step-by-step hint, then retry a similar question.",
        }
    if hints_used >= 2:
        return {
            "next_action": "practice_same_topic",
            "topic": topic,
            "message": "The answer was correct, but the student still needs one more easy practice question.",
        }
    return {
        "next_action": "next_topic",
        "topic": topic,
        "message": "Move to the next topic or a slightly harder question.",
    }


def _update_topic_history(student_id: str, topic: str, is_correct: bool, hints_used: int) -> None:
    stats = _STUDENT_TOPIC_HISTORY[student_id][topic]
    stats["attempts"] += 1
    stats["incorrect"] += 0 if is_correct else 1
    stats["hints_used"] += max(hints_used, 0)


def _normalize_answer(value: str) -> str:
    lowered = value.lower().strip()
    lowered = re.sub(r"[^a-z0-9\s]", " ", lowered)
    lowered = re.sub(r"\b(the|a|an)\b", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered.strip()


def _highlight_keywords(text: str) -> str:
    highlighted = text
    for keyword in _extract_keywords(text)[:3]:
        highlighted = re.sub(
            rf"\b{re.escape(keyword)}\b",
            f"**{keyword}**",
            highlighted,
            count=1,
            flags=re.IGNORECASE,
        )
    return highlighted


def _normalize_spacing(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    unique_items = []
    for item in items:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique_items.append(item)
    return unique_items
