"""Interactive MCQ assessment for EduGen-AI."""
from __future__ import annotations

import re
from typing import Any


def _answer_label(value: Any, options: dict) -> str:
    """Resolve an answer to its A/B/C/D option label."""
    raw = str(value or "").strip()

    match = re.match(r"^\s*([A-D])(?:\s*[.):\-]\s*|\s*$)", raw, re.I)
    if match:
        return match.group(1).upper()

    for label, option_text in options.items():
        if raw.casefold() == str(option_text).strip().casefold():
            return str(label).upper()

    return raw.upper()


def render_quiz(st, bank: dict[str, Any]) -> None:
    """Render an interactive quiz and show score and feedback."""
    if not bank:
        st.info("Generate a Question Bank first, then open the quiz.")
        return

    mcqs = bank.get("mcqs", [])
    topic = str(bank.get("topic", "Study Quiz"))

    st.subheader("🎯 Interactive Quiz & Assessment")
    st.caption(f"Topic: {topic}")

    if not mcqs:
        st.warning("This question bank does not contain any MCQs.")
        return

    topic_key = re.sub(r"\W+", "_", topic).strip("_")[:40] or "quiz"
    form_key = f"assessment_form_{topic_key}"

    answers = {}

    with st.form(form_key):
        for i, question in enumerate(mcqs):
            st.markdown(
                f"**Question {i + 1}. "
                f"{question.get('question', 'Question')}**"
            )

            options = question.get("options", {})
            choices = [
                f"{label}. {options[label]}"
                for label in ["A", "B", "C", "D"]
                if label in options
            ]

            if choices:
                answers[i] = st.radio(
                    "Choose one answer",
                    choices,
                    index=None,
                    key=f"{form_key}_answer_{i}",
                    label_visibility="collapsed",
                )
            else:
                answers[i] = None
                st.warning("Options are unavailable for this question.")

            st.divider()

        submitted = st.form_submit_button(
            "Submit Quiz",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        review = []
        score = 0

        for i, question in enumerate(mcqs):
            options = question.get("options", {})
            selected = _answer_label(answers.get(i), options)
            correct = _answer_label(question.get("answer"), options)

            is_correct = bool(answers.get(i)) and selected == correct
            if is_correct:
                score += 1

            review.append({
                "question": question.get("question", ""),
                "selected": selected or "No answer",
                "correct": correct or "Not provided",
                "is_correct": is_correct,
                "explanation": question.get("explanation", ""),
                "source": question.get("source", "Not specified"),
            })

        st.session_state["assessment_review"] = review
        st.session_state["assessment_score"] = score
        st.session_state["assessment_topic"] = topic

    if st.session_state.get("assessment_topic") == topic:
        review = st.session_state.get("assessment_review", [])
        score = st.session_state.get("assessment_score", 0)

        st.markdown("### 📊 Your Results")
        st.metric("Score", f"{score}/{len(mcqs)}")

        if mcqs:
            st.progress(score / len(mcqs))

        for i, item in enumerate(review, start=1):
            with st.expander(f"Feedback — Question {i}"):
                if item["is_correct"]:
                    st.success("Correct!")
                else:
                    st.error(
                        f"Your answer: {item['selected']} | "
                        f"Correct answer: {item['correct']}"
                    )

                st.write(item["explanation"])
                st.caption(f"Source: {item['source']}")