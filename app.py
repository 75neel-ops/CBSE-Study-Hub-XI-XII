import json
import random
import re
import time
import uuid

import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from PIL import Image, ImageDraw


st.set_page_config(
    page_title="CBSE Study Hub",
    page_icon="📘",
    layout="centered",
)


def make_app_icon():
    """Create a simple logo for the app header."""
    image = Image.new("RGB", (256, 256), "#12345A")
    draw = ImageDraw.Draw(image)

    draw.polygon([(49, 72), (122, 90), (122, 190), (49, 171)], fill="#FFFFFF")
    draw.polygon([(134, 90), (207, 72), (207, 171), (134, 190)], fill="#EAF2F8")
    draw.line([(122, 90), (122, 190)], fill="#12345A", width=7)
    draw.line(
        [(49, 72), (122, 90), (122, 190), (49, 171), (49, 72)],
        fill="#F4B942",
        width=7,
    )
    draw.line(
        [(134, 90), (207, 72), (207, 171), (134, 190), (134, 90)],
        fill="#F4B942",
        width=7,
    )

    for y in (112, 133, 154):
        draw.line([(65, y), (108, y + 5)], fill="#8AA2B8", width=4)
        draw.line([(147, y + 5), (190, y)], fill="#8AA2B8", width=4)

    draw.ellipse((184, 35, 220, 71), fill="#F4B942")
    return image


APP_ICON = make_app_icon()


# Check the current CBSE syllabus before treating this chapter list as definitive.
SUBJECT_CHAPTERS = {
    "Mathematics": {
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
    },
    "Biology": {
        "Class XI": [
            "The Living World",
            "Biological Classification",
            "Plant Kingdom",
            "Animal Kingdom",
            "Morphology of Flowering Plants",
            "Anatomy of Flowering Plants",
            "Structural Organisation in Animals",
            "Cell: The Unit of Life",
            "Biomolecules",
            "Cell Cycle and Cell Division",
            "Photosynthesis in Higher Plants",
            "Respiration in Plants",
            "Plant Growth and Development",
            "Breathing and Exchange of Gases",
            "Body Fluids and Circulation",
            "Excretory Products and Their Elimination",
            "Locomotion and Movement",
            "Neural Control and Coordination",
            "Chemical Coordination and Integration",
        ],
        "Class XII": [
            "Sexual Reproduction in Flowering Plants",
            "Human Reproduction",
            "Reproductive Health",
            "Principles of Inheritance and Variation",
            "Molecular Basis of Inheritance",
            "Evolution",
            "Human Health and Disease",
            "Microbes in Human Welfare",
            "Biotechnology: Principles and Processes",
            "Biotechnology and Its Applications",
            "Organisms and Populations",
            "Ecosystem",
            "Biodiversity and Conservation",
        ],
    },
    "Chemistry": {
        "Class XI": [
            "Some Basic Concepts of Chemistry",
            "Structure of Atom",
            "Classification of Elements and Periodicity in Properties",
            "Chemical Bonding and Molecular Structure",
            "Chemical Thermodynamics",
            "Equilibrium",
            "Redox Reactions",
            "Organic Chemistry: Some Basic Principles and Techniques",
            "Hydrocarbons",
        ],
        "Class XII": [
            "Solutions",
            "Electrochemistry",
            "Chemical Kinetics",
            "The d- and f-Block Elements",
            "Coordination Compounds",
            "Haloalkanes and Haloarenes",
            "Alcohols, Phenols and Ethers",
            "Aldehydes, Ketones and Carboxylic Acids",
            "Amines",
            "Biomolecules",
        ],
    },
    "Physics": {
        "Class XI": [
            "Units and Measurements",
            "Motion in a Straight Line",
            "Motion in a Plane",
            "Laws of Motion",
            "Work, Energy and Power",
            "System of Particles and Rotational Motion",
            "Gravitation",
            "Mechanical Properties of Solids",
            "Mechanical Properties of Fluids",
            "Thermal Properties of Matter",
            "Thermodynamics",
            "Kinetic Theory",
            "Oscillations",
            "Waves",
        ],
        "Class XII": [
            "Electric Charges and Fields",
            "Electrostatic Potential and Capacitance",
            "Current Electricity",
            "Moving Charges and Magnetism",
            "Magnetism and Matter",
            "Electromagnetic Induction",
            "Alternating Current",
            "Electromagnetic Waves",
            "Ray Optics",
            "Wave Optics",
            "Dual Nature of Radiation and Matter",
            "Atoms",
            "Nuclei",
            "Semiconductor Electronics",
        ],
    },
}

DIFFICULTIES = ["Easy", "Hard", "Tricky", "Analytical"]

CBSE_QUESTION_PAPER_URL = (
    "https://www.cbse.gov.in/cbsenew/question-paper.html"
)
CBSE_ACADEMIC_URL = "https://cbseacademic.nic.in/"


def get_openai_client():
    """Create an OpenAI client using the key stored in Streamlit Secrets."""
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        st.error(
            "AI features need an API key. In Streamlit, open your app's "
            "Settings → Secrets and add OPENAI_API_KEY."
        )
        return None

    try:
        return OpenAI(api_key=api_key)
    except Exception as exc:
        st.error(f"Could not initialize the AI service: {exc}")
        return None


def normalize_question(text):
    """Normalize question text to help identify exact repeats."""
    return re.sub(r"\W+", "", str(text).lower())


def generate_keywords(subject, class_name, chapter):
    """Generate and cache a short chapter glossary."""
    cache_key = f"keywords|{subject}|{class_name}|{chapter}"

    if cache_key in st.session_state:
        return st.session_state[cache_key]

    client = get_openai_client()
    if client is None:
        return []

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful CBSE study assistant. "
                        "Return valid JSON only."
                    ),
                },
                {
                    "role": "user",
                    "content": f"""
Create 8 important study keywords for:
Subject: {subject}
Class: {class_name}
Chapter: {chapter}

Return JSON in this format:
{{
  "keywords": [
    {{"term": "keyword", "meaning": "short student-friendly meaning"}}
  ]
}}
Keep meanings concise and appropriate to the specified class.
Do not claim these are official CBSE definitions.
""",
                },
            ],
        )

        data = json.loads(response.choices[0].message.content)
        keywords = data.get("keywords", [])
        st.session_state[cache_key] = keywords
        return keywords

    except Exception as exc:
        st.error(f"Could not generate keywords. Please try again. Details: {exc}")
        return []


def generate_questions(
    subject,
    class_name,
    chapter,
    difficulty,
    count,
    marks,
    previously_seen,
):
    """Generate original subject-specific multiple-choice practice questions."""
    client = get_openai_client()
    if client is None:
        return []

    earlier_questions = previously_seen[-25:]
    earlier_text = "\n".join(f"- {item}" for item in earlier_questions)
    if not earlier_text:
        earlier_text = "No earlier questions."

    prompt = f"""
Create {count} original CBSE-style practice questions.

Subject: {subject}
Class: {class_name}
Chapter: {chapter}
Difficulty: {difficulty}
Marks per question: {marks}

Avoid repeating or closely paraphrasing these earlier questions:
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
- Make questions suitable for the stated subject, class, and chapter.
- Create four options and exactly one correct answer per question.
- The answer is the zero-based index of the correct option.
- Avoid repeating or closely paraphrasing the earlier questions.
- Do not claim the questions are official CBSE questions.
- For numerical questions, ensure the answer and explanation are consistent.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Create accurate educational practice questions. "
                        "Return valid JSON only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        data = json.loads(response.choices[0].message.content)
        valid_questions = []

        for question in data.get("questions", []):
            options = question.get("options")
            answer = question.get("answer")

            if (
                isinstance(question.get("question"), str)
                and isinstance(options, list)
                and len(options) == 4
                and isinstance(answer, int)
                and 0 <= answer < 4
            ):
                question["marks"] = marks
                question["difficulty"] = difficulty
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


# App header and custom logo.
header_col1, header_col2 = st.columns([1, 5], vertical_alignment="center")
with header_col1:
    st.image(APP_ICON, width=72)
with header_col2:
    st.title("CBSE Study Hub")

st.caption("Study and practice for Classes XI and XII")


with st.sidebar:
    # Subtle donation card at the top of the sidebar.
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #f4f8fc, #eef4f8);
            border: 1px solid #d9e4ee;
            border-radius: 12px;
            padding: 12px 13px 8px 13px;
            margin: 0 0 8px 0;
        ">
          <div style="
              color: #173b5e;
              font-size: 15px;
              font-weight: 700;
              margin-bottom: 5px;
          ">Support CBSE Study Hub</div>
          <div style="
              color: #526579;
              font-size: 12px;
              line-height: 1.45;
          ">
            If this app has helped you, you’re welcome to contribute
            any amount you choose. Your support is appreciated.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Razorpay's hosted payment button.
   components.html(
    """
    <html>
      <body style="margin:0; padding:0; overflow:hidden;">
        <form>
          <script
            src="https://checkout.razorpay.com/v1/payment-button.js"
            data-payment_button_id="pl_Tvez6NOZsFJFmN"
            async>
          </script>
        </form>
      </body>
    </html>
    """,
    height=150,
    scrolling=False,
)
    st.caption("App owner: **NilanjanC**")
    st.divider()

    st.header("Choose your subject and chapter")

    class_name = st.selectbox("Class", ["Class XI", "Class XII"])
    subject = st.selectbox(
        "Subject",
        ["Mathematics", "Biology", "Chemistry", "Physics"],
    )
    chapter = st.selectbox(
        "Chapter",
        SUBJECT_CHAPTERS[subject][class_name],
    )
    section = st.radio(
        "Section",
        ["Study keywords", "Quiz practice", "Board papers"],
    )


if section == "Study keywords":
    st.subheader(f"{class_name} {subject} · {chapter}")
    st.write("Generate a short glossary of important chapter terms.")

    if st.button("Show chapter keywords"):
        with st.spinner("Preparing keywords…"):
            keywords = generate_keywords(subject, class_name, chapter)

        if keywords:
            for item in keywords:
                if isinstance(item, dict):
                    st.markdown(f"**{item.get('term', 'Keyword')}**")
                    st.write(item.get("meaning", ""))
                else:
                    st.write(item)

    st.caption(
        "AI-generated definitions are study aids. Check them against your "
        "textbook and the current CBSE syllabus."
    )


elif section == "Quiz practice":
    st.subheader(f"{class_name} {subject} · {chapter}")

    with st.form("quiz_settings"):
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

    if "question_history" not in st.session_state:
        st.session_state.question_history = {}

    history_key = f"{subject}|{class_name}|{chapter}"
    seen_questions = st.session_state.question_history.setdefault(history_key, [])

    if start_quiz:
        st.session_state.quiz_questions = []
        st.session_state.quiz_context = None

        with st.spinner("Creating practice questions…"):
            generated = generate_questions(
                subject=subject,
                class_name=class_name,
                chapter=chapter,
                difficulty=difficulty,
                count=number,
                marks=marks,
                previously_seen=seen_questions,
            )

        seen_keys = {normalize_question(text) for text in seen_questions}
        quiz_keys = set()
        unique_questions = []

        for question in generated:
            key = normalize_question(question["question"])
            if key and key not in seen_keys and key not in quiz_keys:
                unique_questions.append(question)
                quiz_keys.add(key)

        if unique_questions:
            seen_questions.extend(q["question"] for q in unique_questions)

            st.session_state.quiz_questions = unique_questions
            st.session_state.quiz_context = (subject, class_name, chapter)
            st.session_state.quiz_id = str(uuid.uuid4())
            st.session_state.quiz_started = time.time()
            st.session_state.quiz_minutes = minutes
            st.session_state.quiz_submitted = False

            if len(unique_questions) < number:
                st.warning(
                    f"Only {len(unique_questions)} new question(s) were returned. "
                    "Create another quiz to try again."
                )
        elif generated:
            st.warning(
                "The generated questions repeated questions already shown. "
                "Please create the quiz again."
            )

    current_context = (subject, class_name, chapter)

    if (
        st.session_state.get("quiz_questions")
        and st.session_state.get("quiz_context") == current_context
    ):
        questions = st.session_state.quiz_questions
        quiz_id = st.session_state.quiz_id

        elapsed = int(time.time() - st.session_state.quiz_started)
        remaining = max(0, st.session_state.quiz_minutes * 60 - elapsed)

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
                    format_func=lambda option, options=question["options"]: (
                        options[option]
                    ),
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
                    not timed_out
                    and choice is not None
                    and choice == question["answer"]
                ):
                    score += question.get("marks", marks)

            st.session_state.quiz_submitted = True
            st.session_state.quiz_score = score
            st.session_state.quiz_timed_out = timed_out
            st.session_state.quiz_chosen = chosen_answers

        if st.session_state.get("quiz_submitted"):
            if st.session_state.get("quiz_timed_out"):
                st.warning("Time expired. Answers are shown for review.")

            st.success(f"Score: {st.session_state.quiz_score} mark(s)")

            for index, (question, choice) in enumerate(
                zip(questions, st.session_state.quiz_chosen)
            ):
                correct = question["answer"]
                st.markdown(f"**Question {index + 1}:** {question['question']}")

                if choice == correct:
                    st.write("✅ Correct")
                else:
                    st.write(f"❌ Correct answer: {question['options'][correct]}")

                st.write(question.get("explanation", ""))


elif section == "Board papers":
    st.subheader("Official CBSE question papers")

    paper_years = list(range(2025, 2014, -1))
    selected_year = st.selectbox("Choose examination year", paper_years)

    st.write(f"Selected: **{selected_year} · {class_name} · {subject}**")
    st.write(
        "Open the official CBSE question-paper archive, then choose the "
        "matching year, class, and subject from the papers available there."
    )

    st.link_button(
        f"Open CBSE question-paper archive for {selected_year}",
        CBSE_QUESTION_PAPER_URL,
    )

    st.write("For official sample papers and curriculum resources:")
    st.link_button("Open CBSE Academic", CBSE_ACADEMIC_URL)

    st.caption(
        "The year selector helps organize your search, but CBSE controls which "
        "papers are available in its archive. Class XI exams are generally "
        "set by individual schools."
    )


st.divider()
st.caption(
    "AI-generated questions and keywords are study aids, not official CBSE "
    "content. Check them against the current syllabus and trusted textbooks."
)
st.caption("CBSE Study Hub · Owned by NilanjanC")
