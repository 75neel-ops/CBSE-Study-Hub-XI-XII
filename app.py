import copy
import json
import random
import re
import time
import uuid

import streamlit as st


st.set_page_config(
    page_title="CBSE Study Hub",
    page_icon="📘",
    layout="centered",
)


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


# Original starter questions for Mathematics.
# More questions can be added chapter by chapter.
QUESTION_BANK = {
    ("Class XI", "Sets"): [
        {
            "question": "If A = {1, 2, 3} and B = {3, 4, 5}, what is A ∩ B?",
            "options": ["{1, 2}", "{3}", "{4, 5}", "∅"],
            "answer": 1,
            "hint": "The intersection contains elements common to both sets.",
            "explanation": "Only 3 belongs to both A and B, so A ∩ B = {3}.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "If A = {1, 2} and B = {2, 3}, how many elements are in A ∪ B?",
            "options": ["2", "3", "4", "5"],
            "answer": 1,
            "hint": "The union contains each distinct element from both sets.",
            "explanation": "A ∪ B = {1, 2, 3}, so it has 3 elements.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "If A = {1, 2, 3, 4} and B = {2, 4}, find A − B.",
            "options": ["{2, 4}", "{1, 3}", "{1, 2, 3, 4}", "∅"],
            "answer": 1,
            "hint": "A − B contains the elements in A that are not in B.",
            "explanation": "Removing 2 and 4 from A leaves {1, 3}.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "If a set has 3 elements, how many elements are in its power set?",
            "options": ["3", "6", "8", "9"],
            "answer": 2,
            "hint": "A set with n elements has 2ⁿ subsets.",
            "explanation": "The power set has 2³ = 8 elements.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "The universal set is U = {1, 2, 3, 4, 5}. If A = {2, 4}, find A′.",
            "options": ["{2, 4}", "{1, 3, 5}", "{1, 2, 3, 4, 5}", "{3, 5}"],
            "answer": 1,
            "hint": "A′ contains the elements of U that are not in A.",
            "explanation": "Removing 2 and 4 from U leaves {1, 3, 5}.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "If n(A) = 12, n(B) = 9, and n(A ∩ B) = 4, find n(A ∪ B).",
            "options": ["17", "21", "25", "7"],
            "answer": 0,
            "hint": "Use n(A ∪ B) = n(A) + n(B) − n(A ∩ B).",
            "explanation": "n(A ∪ B) = 12 + 9 − 4 = 17.",
            "difficulty": "Analytical",
            "marks": 2,
        },
        {
            "question": "Which statement is always true for any set A?",
            "options": ["A ∪ ∅ = ∅", "A ∩ ∅ = A", "A ∪ ∅ = A", "A − A = A"],
            "answer": 2,
            "hint": "The empty set contributes no elements to a union.",
            "explanation": "Taking the union of A with the empty set leaves A unchanged.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "If A = {1, 2, 3} and B = {3, 4}, find A △ B, the symmetric difference.",
            "options": ["{3}", "{1, 2, 4}", "{1, 2, 3, 4}", "∅"],
            "answer": 1,
            "hint": "The symmetric difference contains elements in exactly one of the sets.",
            "explanation": "The common element 3 is excluded. The result is {1, 2, 4}.",
            "difficulty": "Tricky",
            "marks": 2,
        },
        {
            "question": "If A ⊆ B and B ⊆ A, what can be concluded?",
            "options": ["A ∩ B = ∅", "A = B", "A is a proper subset of B", "B = ∅"],
            "answer": 1,
            "hint": "Each set contains all the elements of the other.",
            "explanation": "Mutual inclusion means the two sets have exactly the same elements.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "How many subsets does the empty set have?",
            "options": ["0", "1", "2", "It depends on the universal set"],
            "answer": 1,
            "hint": "The empty set is a subset of every set, including itself.",
            "explanation": "The only subset of ∅ is ∅ itself, so it has one subset.",
            "difficulty": "Tricky",
            "marks": 1,
        },
        {
            "question": "If n(A) = 20, n(B) = 15, and n(A ∪ B) = 28, find n(A ∩ B).",
            "options": ["5", "7", "13", "35"],
            "answer": 1,
            "hint": "Rearrange the formula for the number of elements in a union.",
            "explanation": "n(A ∩ B) = 20 + 15 − 28 = 7.",
            "difficulty": "Analytical",
            "marks": 2,
        },
        {
            "question": "Which identity is De Morgan's law for the complement of a union?",
            "options": [
                "(A ∪ B)′ = A′ ∪ B′",
                "(A ∪ B)′ = A′ ∩ B′",
                "(A ∩ B)′ = A′ ∩ B′",
                "A ∪ A′ = ∅",
            ],
            "answer": 1,
            "hint": "The complement switches union to intersection.",
            "explanation": "De Morgan's law states that (A ∪ B)′ = A′ ∩ B′.",
            "difficulty": "Tricky",
            "marks": 1,
        },
        {
            "question": "If A = {x : x is a positive integer less than 5}, which is A?",
            "options": ["{0, 1, 2, 3, 4}", "{1, 2, 3, 4}", "{1, 2, 3, 4, 5}", "{2, 3, 4}"],
            "answer": 1,
            "hint": "Positive integers start at 1; include those less than 5.",
            "explanation": "The positive integers less than 5 are 1, 2, 3, and 4.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "Let A = {1, 2, 3, 4} and B = {3, 4, 5}. What is A ∩ B?",
            "options": ["{1, 2}", "{3, 4}", "{1, 2, 5}", "{1, 2, 3, 4, 5}"],
            "answer": 1,
            "hint": "Find the elements appearing in both sets.",
            "explanation": "The common elements are 3 and 4.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "If n(A) = 8 and n(B) = 6, what is the greatest possible value of n(A ∩ B)?",
            "options": ["0", "2", "6", "14"],
            "answer": 2,
            "hint": "The intersection cannot contain more elements than the smaller set.",
            "explanation": "The greatest possible intersection is the size of the smaller set, 6.",
            "difficulty": "Analytical",
            "marks": 2,
        },
    ],

    ("Class XI", "Relations and Functions"): [
        {
            "question": "If f(x) = 2x + 3, find f(4).",
            "options": ["8", "11", "14", "5"],
            "answer": 1,
            "hint": "Substitute x = 4 into the function.",
            "explanation": "f(4) = 2(4) + 3 = 11.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "What is the domain of f(x) = 1/(x − 2) over the real numbers?",
            "options": [
                "All real numbers",
                "All real numbers except 0",
                "All real numbers except 2",
                "x > 2 only",
            ],
            "answer": 2,
            "hint": "The denominator of a fraction cannot be zero.",
            "explanation": "x − 2 must not equal zero, so x ≠ 2.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "If f(x) = x², what is f(−3)?",
            "options": ["−9", "−6", "6", "9"],
            "answer": 3,
            "hint": "Square the input, including its sign.",
            "explanation": "f(−3) = (−3)² = 9.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "If f(x) = 3x − 1, for what value of x is f(x) = 8?",
            "options": ["2", "3", "4", "9"],
            "answer": 1,
            "hint": "Solve the equation 3x − 1 = 8.",
            "explanation": "3x − 1 = 8 gives 3x = 9, so x = 3.",
            "difficulty": "Analytical",
            "marks": 2,
        },
        {
            "question": "Which relation on a set A is called the identity relation?",
            "options": [
                "{(a, b) : a ≠ b}",
                "{(a, a) : a ∈ A}",
                "A × A",
                "∅",
            ],
            "answer": 1,
            "hint": "In the identity relation, each element is related to itself.",
            "explanation": "The identity relation consists of all ordered pairs (a, a) for a in A.",
            "difficulty": "Easy",
            "marks": 1,
        },
    ],

    ("Class XII", "Matrices"): [
        {
            "question": "Find the determinant of [[1, 2], [3, 4]].",
            "options": ["−2", "2", "10", "−10"],
            "answer": 0,
            "hint": "For [[a, b], [c, d]], the determinant is ad − bc.",
            "explanation": "(1 × 4) − (2 × 3) = 4 − 6 = −2.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "If A is a 2 × 3 matrix and B is a 3 × 4 matrix, what is the order of AB?",
            "options": ["3 × 3", "2 × 4", "4 × 2", "2 × 3"],
            "answer": 1,
            "hint": "For a product, the outer dimensions give the order.",
            "explanation": "A(2 × 3) multiplied by B(3 × 4) gives a 2 × 4 matrix.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "If A = [[1, 2], [3, 4]], what is the element in the second row and first column?",
            "options": ["1", "2", "3", "4"],
            "answer": 2,
            "hint": "Read the row first, then the column.",
            "explanation": "The element in row 2, column 1 is 3.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "If A is a 2 × 3 matrix, what is the order of its transpose Aᵀ?",
            "options": ["2 × 3", "3 × 2", "2 × 2", "3 × 3"],
            "answer": 1,
            "hint": "The transpose swaps rows and columns.",
            "explanation": "A 2 × 3 matrix becomes a 3 × 2 matrix when transposed.",
            "difficulty": "Easy",
            "marks": 1,
        },
    ],

    ("Class XII", "Determinants"): [
        {
            "question": "Evaluate the determinant |1  2; 3  4|.",
            "options": ["−2", "2", "10", "0"],
            "answer": 0,
            "hint": "For a 2 × 2 determinant, calculate ad − bc.",
            "explanation": "(1 × 4) − (2 × 3) = −2.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "What is the value of the determinant |2  0; 0  5|?",
            "options": ["7", "10", "0", "25"],
            "answer": 1,
            "hint": "For a diagonal 2 × 2 matrix, multiply the diagonal entries.",
            "explanation": "(2 × 5) − (0 × 0) = 10.",
            "difficulty": "Easy",
            "marks": 1,
        },
        {
            "question": "If two rows of a determinant are identical, what is its value?",
            "options": ["1", "−1", "0", "It cannot be determined"],
            "answer": 2,
            "hint": "Consider what happens to a determinant when two rows are equal.",
            "explanation": "A determinant with two identical rows has value 0.",
            "difficulty": "Tricky",
            "marks": 1,
        },
    ],
}


DIFFICULTIES = ["Easy", "Hard", "Tricky", "Analytical"]


def normalize_question(question_text):
    """Normalize text to help detect exact repeated questions."""
    return re.sub(r"\W+", "", str(question_text).lower())


def get_question_history():
    """Keep question history in the current Streamlit session."""
    if "question_history" not in st.session_state:
        st.session_state.question_history = {}
    return st.session_state.question_history


def generate_ai_questions(
    class_name,
    chapter,
    difficulty,
    count,
    marks,
    previously_seen_questions,
):
    """Generate original practice questions using Streamlit Secrets."""
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        st.error(
            "AI questions need an API key. In Streamlit, open your app's "
            "Settings → Secrets and add OPENAI_API_KEY."
        )
        return []

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        earlier_questions = previously_seen_questions[-25:]
        earlier_text = "\n".join(f"- {question}" for question in earlier_questions)
        if not earlier_text:
            earlier_text = "No earlier questions."

        prompt = f"""
Create {count} original CBSE-style Mathematics practice questions.

Class: {class_name}
Chapter: {chapter}
Difficulty: {difficulty}
Marks per question: {marks}

Do not repeat or closely paraphrase any of these questions:
{earlier_text}

Return only valid JSON in this format:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": 0,
      "hint": "A short hint that does not give away the answer",
      "explanation": "A clear explanation",
      "difficulty": "{difficulty}",
      "marks": {marks}
    }}
  ]
}}

Requirements:
- Create exactly {count} questions if possible.
- Every question must have exactly four options and one correct answer.
- The answer must be the zero-based index of the correct option.
- Make questions appropriate for the stated class and chapter.
- Avoid repeating the earlier questions, including close paraphrases.
- Do not claim these are official CBSE questions.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Create accurate educational Mathematics practice questions. "
                        "Return valid JSON only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        response_text = response.choices[0].message.content
        data = json.loads(response_text)
        questions = data.get("questions", [])

        valid_questions = []

        for question in questions:
            options = question.get("options")
            answer = question.get("answer")

            if (
                isinstance(question.get("question"), str)
                and isinstance(options, list)
                and len(options) == 4
                and isinstance(answer, int)
                and 0 <= answer < 4
            ):
                question["difficulty"] = difficulty
                question["marks"] = marks
                question.setdefault("hint", "Try identifying the key idea first.")
                question.setdefault(
                    "explanation",
                    "Review the relevant chapter concept.",
                )
                valid_questions.append(question)

        return valid_questions

    except Exception as exc:
        st.error(f"Could not generate questions. Please try again. Details: {exc}")
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
        "Verified chapter notes and keywords will be added here as the study "
        "content is prepared."
    )
    st.markdown(
        "**Study tip:** Write each definition in your own words, "
        "then test yourself without looking."
    )


elif section == "Quiz practice":
    st.subheader(f"Quiz · {chapter}")

    with st.form("quiz_settings"):
        source = st.selectbox(
            "Question source",
            ["Curated bank", "AI-generated practice"],
        )

        difficulty = st.selectbox("Difficulty", DIFFICULTIES)
        marks = st.selectbox("Marks per question", [1, 2, 3, 4, 5])
        number = st.slider(
            "Number of questions",
            min_value=1,
            max_value=10,
            value=3,
        )
        minutes = st.selectbox("Time limit (minutes)", [5, 10, 15, 20, 30])

        start_quiz = st.form_submit_button("Create quiz")

    history = get_question_history()
    history_key = f"{class_name}|{chapter}|{source}"
    seen_questions = history.setdefault(history_key, [])

    if start_quiz:
        # Clear the old displayed quiz while creating a new one.
        st.session_state.quiz_context = None
        st.session_state.quiz_questions = []

        seen_keys = {
            normalize_question(text)
            for text in seen_questions
        }

        if source == "Curated bank":
            available = QUESTION_BANK.get((class_name, chapter), [])

            matching_difficulty = [
                question
                for question in available
                if question.get("difficulty") == difficulty
            ]

            # If this chapter has no questions at the selected difficulty,
            # use its other curated questions.
            if matching_difficulty:
                available = matching_difficulty

            unseen_questions = [
                question
                for question in available
                if normalize_question(question["question"]) not in seen_keys
            ]

            if not unseen_questions:
                if not available:
                    st.warning(
                        "There are no curated questions for this chapter yet. "
                        "Choose AI-generated practice or use a chapter with "
                        "curated questions."
                    )
                else:
                    st.warning(
                        "You have seen all the curated questions currently "
                        "available for this chapter in this session."
                    )
            else:
                selected_questions = random.sample(
                    unseen_questions,
                    min(number, len(unseen_questions)),
                )

                # Apply the selected marks setting to each selected question.
                for question in selected_questions:
                    question["marks"] = marks

                seen_questions.extend(
                    question["question"]
                    for question in selected_questions
                )

                st.session_state.quiz_questions = selected_questions
                st.session_state.quiz_context = (
                    class_name,
                    chapter,
                    source,
                )
                st.session_state.quiz_id = str(uuid.uuid4())
                st.session_state.quiz_started = time.time()
                st.session_state.quiz_minutes = minutes
                st.session_state.quiz_submitted = False

                if len(selected_questions) < number:
                    st.info(
                        f"Only {len(selected_questions)} unseen curated "
                        "question(s) are currently available."
                    )

        else:
            with st.spinner("Creating practice questions…"):
                generated_questions = generate_ai_questions(
                    class_name=class_name,
                    chapter=chapter,
                    difficulty=difficulty,
                    count=number,
                    marks=marks,
                    previously_seen_questions=seen_questions,
                )

            unique_questions = []
            keys_in_this_quiz = set()

            for question in generated_questions:
                key = normalize_question(question["question"])

                if (
                    key
                    and key not in seen_keys
                    and key not in keys_in_this_quiz
                ):
                    unique_questions.append(question)
                    keys_in_this_quiz.add(key)

            if unique_questions:
                seen_questions.extend(
                    question["question"]
                    for question in unique_questions
                )

                st.session_state.quiz_questions = unique_questions
                st.session_state.quiz_context = (
                    class_name,
                    chapter,
                    source,
                )
                st.session_state.quiz_id = str(uuid.uuid4())
                st.session_state.quiz_started = time.time()
                st.session_state.quiz_minutes = minutes
                st.session_state.quiz_submitted = False

                if len(unique_questions) < number:
                    st.warning(
                        f"Only {len(unique_questions)} new question(s) were "
                        "available. Try creating another quiz."
                    )

            elif generated_questions:
                st.warning(
                    "The generated questions matched questions already shown. "
                    "Please create the quiz again."
                )

    current_context = (class_name, chapter, source)
    quiz_context = st.session_state.get("quiz_context")

    if (
        st.session_state.get("quiz_questions")
        and quiz_context == current_context
    ):
        questions = st.session_state.quiz_questions
        quiz_id = st.session_state.quiz_id

        elapsed = int(time.time() - st.session_state.quiz_started)
        remaining = max(
            0,
            st.session_state.quiz_minutes * 60 - elapsed,
        )

        st.caption(
            f"Time remaining when you submit: "
            f"{remaining // 60}:{remaining % 60:02d}"
        )

        with st.form(f"answer_quiz_{quiz_id}"):
            chosen_answers = []

            for index, question in enumerate(questions):
                st.markdown(
                    f"**Question {index + 1} · "
                    f"{question.get('marks', marks)} mark(s)**"
                )
                st.write(question["question"])

                with st.expander("Show hint"):
                    st.write(question.get("hint", "No hint available."))

                choice = st.radio(
                    "Choose an answer",
                    options=list(range(len(question["options"]))),
                    format_func=lambda option, options=question["options"]: options[option],
                    key=f"{quiz_id}_answer_{index}",
                    index=None,
                )
                chosen_answers.append(choice)

            submitted = st.form_submit_button("Submit answers")

        if submitted:
            elapsed = int(time.time() - st.session_state.quiz_started)
            timed_out = elapsed > st.session_state.quiz_minutes * 60
            score = 0

            for question, choice in zip(questions, chosen_answers):
                if (
                    choice is not None
                    and choice == question["answer"]
                    and not timed_out
                ):
                    score += question.get("marks", marks)

            st.session_state.quiz_submitted = True
            st.session_state.quiz_score = score
            st.session_state.quiz_timed_out = timed_out
            st.session_state.quiz_chosen = chosen_answers

        if st.session_state.get("quiz_submitted"):
            if st.session_state.get("quiz_timed_out"):
                st.warning(
                    "Time expired before submission. Answers are shown for "
                    "review, but no marks were awarded."
                )

            st.success(f"Score: {st.session_state.quiz_score} mark(s)")

            for index, (question, choice) in enumerate(
                zip(questions, st.session_state.quiz_chosen)
            ):
                correct_answer = question["answer"]

                st.markdown(
                    f"**Question {index + 1}:** {question['question']}"
                )

                if choice == correct_answer:
                    st.write("✅ Correct")
                else:
                    st.write(
                        f"❌ Correct answer: "
                        f"{question['options'][correct_answer]}"
                    )

                st.write(question.get("explanation", ""))


elif section == "Board papers":
    st.subheader("Official CBSE question papers")

    st.write(
        "Open CBSE's official question-paper archive to look for original "
        "papers by class, subject, and year."
    )

    st.link_button(
        "Open official CBSE question-paper archive",
        "https://www.cbse.gov.in/cbsenew/question-paper.html",
    )

    st.caption(
        "Class XII has CBSE board examination papers. Class XI examinations "
        "are generally set by individual schools."
    )


st.divider()
st.caption(
    "AI-generated questions are for practice, are not official CBSE questions, "
    "and should be checked against the current syllabus and trusted materials."
)
