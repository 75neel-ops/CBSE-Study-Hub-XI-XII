import json
import random
import time

import streamlit as st

st.set_page_config(page_title="CBSE Study Hub", page_icon="📘", layout="centered")

# Check the latest CBSE syllabus before treating this chapter list as definitive.
CHAPTERS = {
    "Class XI": [
        "Sets",
        "Relations and Functions",
        "Trigonometric Functions",
        "Complex Numbers and Quadratic Equations",
        "Linear Inequalities",
        "Permutations and Combinations",
        "Binomial Theorem",
        "Sequence and Series",
        "Straight Lines",
        "Conic Sections",
        "Introduction to 3D Geometry",
        "Limits and Derivatives",
        "Statistics",
        "Probability",
    ],
    "Class XII": [
        "Relations and Functions",
        "Inverse Trigonometric Functions",
        "Matrices",
        "Determinants",
        "Continuity and Differentiability",
        "Application of Derivatives",
        "Integrals",
        "Application of Integrals",
        "Differential Equations",
        "Vector Algebra",
        "Three Dimensional Geometry",
        "Linear Programming",
        "Probability",
    ],
}

# Original starter examples. Expand this bank with reviewed questions.
QUESTION_BANK = {
    ("Class XI", "Sets"): [
        {
            "question": "If A = {1, 2} and B = {2, 3}, how many elements are in A ∪ B?",
            "options": ["2", "3", "4", "5"],
            "answer": 1,
            "hint": "The union contains each distinct element from both sets.",
            "explanation": "A ∪ B = {1, 2, 3}, so it has 3 elements.",
            "difficulty": "Easy",
            "marks": 1,
        }
    ],
    ("Class XII", "Matrices"): [
        {
            "question": "Find the determinant of [[1, 2], [3, 4]].",
            "options": ["-2", "2", "10", "-10"],
            "answer": 0,
            "hint": "For [[a, b], [c, d]], the determinant is ad − bc.",
            "explanation": "(1 × 4) − (2 × 3) = 4 − 6 = -2.",
            "difficulty": "Easy",
            "marks": 1,
        }
    ],
}

DIFFICULTIES = ["Easy", "Hard", "Tricky", "Analytical"]


def generate_ai_questions(class_name, chapter, difficulty, count, marks):
    """Generate practice questions using an API key stored in Streamlit Secrets."""
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        st.error(
            "AI questions need an API key. Add OPENAI_API_KEY in "
            "your Streamlit app's Settings → Secrets."
        )
        return []

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = f"""
Create {count} original CBSE-style Mathematics practice questions.
Class: {class_name}
Chapter: {chapter}
Difficulty: {difficulty}
Marks per question: {marks}

Return only valid JSON in this exact structure:
{{
  "questions": [
    {{
      "question": "question text",
      "options": ["A", "B", "C", "D"],
      "answer": 0,
      "hint": "short hint",
      "explanation": "step-by-step explanation",
      "difficulty": "{difficulty}",
      "marks": {marks}
    }}
  ]
}}
The answer field must be the zero-based index of the correct option.
Ensure each question has exactly four options and one correct answer.
Keep questions appropriate to the stated class and chapter.
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "Create accurate educational practice questions. Return valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        data = json.loads(response.choices[0].message.content)
        questions = data.get("questions", [])

        # Basic validation before showing AI output.
        valid = []
        for q in questions:
            if (
                isinstance(q.get("question"), str)
                and isinstance(q.get("options"), list)
                and len(q["options"]) == 4
                and isinstance(q.get("answer"), int)
                and 0 <= q["answer"] < 4
            ):
                q["marks"] = marks
                q["difficulty"] = difficulty
                valid.append(q)
        return valid

    except Exception as exc:
        st.error(f"Could not generate questions: {exc}")
        return []


st.title("📘 CBSE Study Hub")
st.caption("Mathematics practice for Classes XI and XII")

with st.sidebar:
    st.header("Choose your chapter")
    class_name = st.selectbox("Class", list(CHAPTERS.keys()))
    chapter = st.selectbox("Chapter", CHAPTERS[class_name])
    section = st.radio(
        "Section",
        ["Study keywords", "Quiz practice", "Board papers"],
    )

if section == "Study keywords":
    st.subheader(f"{class_name} Mathematics · {chapter}")
    st.info(
        "Chapter notes and a reviewed keyword bank will be added chapter by chapter. "
        "For now, this section is a placeholder for verified study material."
    )
    st.markdown("**Study tip:** Write each definition in your own words, then test yourself without looking.")

elif section == "Quiz practice":
    st.subheader(f"Quiz · {chapter}")

    with st.form("quiz_settings"):
        source = st.selectbox(
            "Question source",
            ["Curated bank", "AI-generated practice"],
        )
        difficulty = st.selectbox("Difficulty", DIFFICULTIES)
        marks = st.selectbox("Marks per question", [1, 2, 3, 4, 5])
        number = st.slider("Number of questions", 1, 10, 3)
        minutes = st.selectbox("Time limit (minutes)", [5, 10, 15, 20, 30])
        start_quiz = st.form_submit_button("Create quiz")

    if start_quiz:
        if source == "Curated bank":
            available = QUESTION_BANK.get((class_name, chapter), [])
            questions = [q for q in available if q["difficulty"] == difficulty]
            if not questions:
                questions = available
            questions = random.sample(questions, min(number, len(questions)))
            if not questions:
                st.warning(
                    "There are no curated questions for this chapter yet. "
                    "Choose AI-generated practice or add reviewed questions to the bank."
                )
            else:
                st.session_state.quiz_questions = questions
                st.session_state.quiz_started = time.time()
                st.session_state.quiz_minutes = minutes
                st.session_state.quiz_submitted = False

        else:
            with st.spinner("Creating practice questions…"):
                questions = generate_ai_questions(
                    class_name, chapter, difficulty, number, marks
                )
            if questions:
                st.session_state.quiz_questions = questions
                st.session_state.quiz_started = time.time()
                st.session_state.quiz_minutes = minutes
                st.session_state.quiz_submitted = False

    questions = st.session_state.get("quiz_questions", [])
    if questions:
        elapsed = int(time.time() - st.session_state.quiz_started)
        remaining = max(
            0, st.session_state.quiz_minutes * 60 - elapsed
        )
        st.caption(
            f"Time remaining when you submit: "
            f"{remaining // 60}:{remaining % 60:02d}"
        )

        with st.form("answer_quiz"):
            chosen_answers = []
            for i, q in enumerate(questions):
                st.markdown(f"**Question {i + 1} · {q.get('marks', marks)} mark(s)**")
                st.write(q["question"])
                with st.expander("Show hint"):
                    st.write(q.get("hint", "No hint available."))
                choice = st.radio(
                    "Choose an answer",
                    range(len(q["options"])),
                    format_func=lambda n, opts=q["options"]: opts[n],
                    key=f"answer_{i}",
                    index=None,
                )
                chosen_answers.append(choice)

            submitted = st.form_submit_button("Submit answers")

        if submitted:
            elapsed = int(time.time() - st.session_state.quiz_started)
            timed_out = elapsed > st.session_state.quiz_minutes * 60
            score = 0

            for q, choice in zip(questions, chosen_answers):
                if choice is not None and choice == q["answer"] and not timed_out:
                    score += q.get("marks", marks)

            st.session_state.quiz_submitted = True
            st.session_state.quiz_score = score
            st.session_state.quiz_timed_out = timed_out
            st.session_state.quiz_chosen = chosen_answers

        if st.session_state.get("quiz_submitted"):
            if st.session_state.get("quiz_timed_out"):
                st.warning("Time expired before submission. Answers are shown for review.")
            st.success(f"Score: {st.session_state.quiz_score} marks")

            for i, (q, choice) in enumerate(
                zip(questions, st.session_state.quiz_chosen)
            ):
                correct = q["answer"]
                st.markdown(f"**Question {i + 1}:** {q['question']}")
                if choice == correct:
                    st.write("✅ Correct")
                else:
                    st.write(f"❌ Correct answer: {q['options'][correct]}")
                st.write(q.get("explanation", ""))

elif section == "Board papers":
    st.subheader("CBSE Mathematics papers")
    st.write(
        "Use CBSE's official academic website to find available sample papers "
        "and examination resources."
    )
    st.link_button(
        "Open CBSE Academic website",
        "https://cbseacademic.nic.in/",
    )
    st.info(
        "Class XII board papers can be listed here by year as verified links are added. "
        "Class XI exams are generally conducted by schools, so this section can also "
        "include school-style practice papers."
    )

st.divider()
st.caption(
    "AI-generated questions are for practice and should be checked against the "
    "current CBSE syllabus and trusted study materials."
)
