from __future__ import annotations

import hashlib
import os
from pathlib import Path
from collections import Counter

import streamlit as st
from document_pipeline import process_document
from retrieval import search_chunks, retrieval_engine_name
from llm import explain_topic
from question_bank import generate_question_bank
from content_synthesis import synthesize_content
from assessment import render_quiz

st.set_page_config(
    page_title="EduGen AI | Academic Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).parent
SAMPLE_DIR = ROOT / "sample_docs"
CATEGORIES = ["All", "Notes", "Textbook", "Questions", "Labs", "Other"]

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
      .stApp { background: #f6f8fc; font-family: 'DM Sans', sans-serif; }
      .block-container { max-width: 1240px; padding-top: 1.25rem; padding-bottom: 2.5rem; }
      [data-testid="stSidebar"] { background: #10172a; }
      [data-testid="stSidebar"] * { color: #edf2ff; }
      [data-testid="stSidebar"] [data-testid="stRadio"] label { color: #e5e7eb; }
      .hero { background: linear-gradient(120deg,#111827 0%,#253a78 55%,#5b43c7 100%); padding: 30px 34px; border-radius: 22px; color: white; margin-bottom: 24px; box-shadow: 0 16px 38px rgba(31,41,95,.18); }
      .hero .eyebrow { text-transform: uppercase; letter-spacing: .14em; font-size: 11px; font-weight: 700; color: #c7d2fe; margin-bottom: 8px; }
      .hero h1 { font-family: 'Space Grotesk', sans-serif; color: white; font-size: clamp(30px,4vw,45px); line-height: 1.08; margin: 0; }
      .hero p { color: #e0e7ff; max-width: 760px; font-size: 16px; margin: 12px 0 0; }
      .eyebrow-dark { color: #4f46e5; text-transform: uppercase; letter-spacing: .12em; font-size: 11px; font-weight: 700; }
      .small-muted { color: #64748b; font-size: 13px; }
      [data-testid="stMetric"] { background: #fff; border: 1px solid #e7eaf2; border-radius: 15px; padding: 15px 18px; box-shadow: 0 4px 12px rgba(24,39,75,.035); }
      [data-testid="stMetricLabel"] { color: #64748b; }
      div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] { background: linear-gradient(90deg,#4f46e5,#6d5ce8); border: 0; color: white; font-weight: 700; border-radius: 10px; min-height: 44px; }
      div.stButton > button { border-radius: 10px; }
      h1,h2,h3 { font-family: 'Space Grotesk', sans-serif; }
      [data-testid="stExpander"] { background: #fff; border-radius: 12px; border: 1px solid #e7eaf2; }
      .tagline { color: #94a3b8; font-size: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Durable only for the current Streamlit browser session.
for key, default in {
    "chunks": [],
    "processed_docs": [],
    "file_hashes": set(),
    "last_question": "",
    "last_results": [],
    "last_answer": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "")
    try:
        key = key or str(st.secrets.get("GEMINI_API_KEY", ""))
    except Exception:
        pass
    return key.strip()


def get_gemini_model() -> str:
    model = os.getenv("GEMINI_MODEL", "")
    try:
        model = model or str(st.secrets.get("GEMINI_MODEL", ""))
    except Exception:
        pass
    return model.strip()


def go_to(page: str) -> None:
    st.session_state.navigation = page


def render_source_card(item: dict, number: int) -> None:
    source = item.get("source", "Unknown source")
    category = item.get("category", "Other")
    page = item.get("page", "?")
    location_type = item.get("location_type", "page")
    score = item.get("score")
    score_text = f" · Match {score:.2f}" if isinstance(score, (int, float)) else ""
    with st.container(border=True):
        st.markdown(f"**[S{number}] {source}**")
        st.caption(f"{category} · {location_type.title()} {page}{score_text}")
        st.write(item.get("text", ""))


with st.sidebar:
    st.markdown("# 🎓 EduGen AI")
    st.markdown("<div class='tagline'>YOUR ACADEMIC KNOWLEDGE DESK</div>", unsafe_allow_html=True)
    st.divider()
    page = st.radio(
        "WORKSPACE",
["Dashboard", "Upload & Process", "Explain a Topic", "Question Bank", "Content Synthesis", "Document Library"],        label_visibility="visible",
    )
    st.divider()
 
st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">MULTI-DOCUMENT ACADEMIC ASSISTANT</div>
      <h1>Turn study material into understanding.</h1>
      <p>Upload notes, textbooks, question banks and lab manuals. Ask one topic-based question and explore evidence from your own documents—with source references.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "Dashboard":
    docs = st.session_state.processed_docs
    chunks = st.session_state.chunks
    unique_sources = len({str(c.get("source")) for c in chunks})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Documents processed", len(docs))
    c2.metric("Searchable chunks", len(chunks))
    c3.metric("Source files indexed", unique_sources)
    c4.metric("Supported formats", "PDF · DOCX · PPTX")

    st.subheader("Start here")
    with st.container(border=True):
        st.markdown("#### 📚 01 · Build your knowledge base")
        st.write("Upload several academic files together. EduGen-AI extracts text, assigns a category, and keeps page/slide/section metadata.")
        st.button("Upload study material →", type="primary", use_container_width=True, on_click=go_to, args=("Upload & Process",))
    with st.container(border=True):
        st.markdown("#### ✨ 02 · Explain a topic")
        st.write("Ask a question such as *Explain CPU scheduling using my notes and textbook*. Review the explanation and open every cited excerpt.")
        st.button("Open topic explainer →", use_container_width=True, on_click=go_to, args=("Explain a Topic",))

    if not docs:
        st.info("Tip: start by uploading at least two sources on the same topic (for example, Operating Systems notes + a question bank). This makes the multi-source demo much stronger.")
    else:
        st.subheader("Your current knowledge base")
        st.dataframe(docs, use_container_width=True, hide_index=True)

    st.subheader("Optional sample files for a quick demo")
    st.caption("Download these sample files to your computer, then upload all of them in Upload & Process. They cover the same CPU scheduling topic across different academic categories and file formats.")
    sample_files = sorted(SAMPLE_DIR.glob("*")) if SAMPLE_DIR.exists() else []
    if sample_files:
        cols = st.columns(min(4, len(sample_files)))
        for i, sample in enumerate(sample_files):
            with cols[i % len(cols)]:
                st.download_button(
                    f"Download {sample.suffix.upper()} · {sample.stem.replace('_', ' ')}",
                    data=sample.read_bytes(),
                    file_name=sample.name,
                    mime={".pdf": "application/pdf", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation"}.get(sample.suffix.lower(), "application/octet-stream"),
                    key=f"sample_{sample.name}",
                    use_container_width=True,
                )

elif page == "Upload & Process":
    st.subheader("📚 Upload academic sources")
    st.write("Select several files at once. Each file is processed separately and indexed with its source name and location metadata.")
    uploaded_files = st.file_uploader(
        "Choose PDF, Word, or PowerPoint files",
        type=["pdf", "docx", "pptx"],
        accept_multiple_files=True,
        help="Text-based PDFs work best. Scanned/image-only PDFs need OCR, which is not included in this first milestone.",
    )
    a, b = st.columns(2)
    with a:
        chunk_size = st.select_slider("Chunk size", options=[500, 700, 900, 1200, 1500], value=900)
    with b:
        overlap = st.select_slider("Overlap", options=[0, 50, 100, 120, 150, 200], value=120)
    subject_col, chapter_col = st.columns(2)

    with subject_col:
        subject_name = st.text_input(
            "Subject",
            placeholder="e.g., Software Engineering",
            key="upload_subject",
        )

    with chapter_col:
        chapter_name = st.text_input(
            "Chapter / Unit",
            placeholder="e.g., Software Requirements",
            key="upload_chapter",
        )
    if st.button("Process & index files", type="primary", disabled=not uploaded_files):
        progress = st.progress(0)
        status = st.empty()
        added_count = 0
        skipped_count = 0
        errors: list[str] = []
        for idx, uploaded in enumerate(uploaded_files):
            payload = uploaded.getvalue()
            digest = hashlib.sha256(payload).hexdigest()
            if digest in st.session_state.file_hashes:
                skipped_count += 1
                progress.progress((idx + 1) / len(uploaded_files))
                continue
            try:
                uploaded.seek(0)
                new_chunks = process_document(uploaded, chunk_size=int(chunk_size), overlap=int(overlap))
                if not new_chunks:
                    errors.append(f"{uploaded.name}: no extractable text found. If this is a scanned PDF, use a text-based PDF or OCR first.")
               
                else:
                    subject_value = subject_name.strip() or "Unassigned"
                    chapter_value = chapter_name.strip() or "Unassigned"

                    for chunk in new_chunks:
                        chunk["subject"] = subject_value
                        chunk["chapter"] = chapter_value
                    st.session_state.chunks.extend(new_chunks)

                    # Week 5: Programming code detection summary
                    code_chunks = [
                        chunk for chunk in new_chunks
                        if chunk.get("contains_code", False)
                    ]

                    detected_languages = sorted({
                        language
                        for chunk in code_chunks
                        for language in chunk.get("programming_languages", [])
                    })

                    if code_chunks:
                        st.info(
                            f"Code detected in {len(code_chunks)} chunk(s). "
                            f"Languages: {', '.join(detected_languages) or 'Unknown'}"
                        )
                    else:
                        st.caption("No recognizable programming code detected in this file.")

                    category = new_chunks[0].get("category", "Other")
                    st.session_state.processed_docs.append({
                        "name": uploaded.name,
                        "format": uploaded.name.rsplit(".", 1)[-1].upper(),
                        "category": category,
                        "subject": subject_value,
                        "chapter": chapter_value,
                        "chunks": len(new_chunks),
                        "locations": len({c.get("page") for c in new_chunks}),
                        "size_kb": round(len(payload) / 1024, 1),
                    })
                    st.session_state.file_hashes.add(digest)
                    added_count += 1
            except Exception as exc:
                errors.append(f"{uploaded.name}: {type(exc).__name__}: {exc}")
            progress.progress((idx + 1) / len(uploaded_files))
            status.caption(f"Processed {idx + 1} of {len(uploaded_files)} file(s)")
        if added_count:
            st.success(f"Indexed {added_count} new file(s) into {sum(1 for c in st.session_state.chunks)} total text chunks.")
        if skipped_count:
            st.info(f"Skipped {skipped_count} duplicate file(s) already in this browser session.")
        for err in errors:
            st.error(err)

    if st.session_state.processed_docs:
        st.subheader("Processing report")
        st.dataframe(st.session_state.processed_docs, use_container_width=True, hide_index=True)
        category_counts = Counter(d["category"] for d in st.session_state.processed_docs)
        st.caption("Auto-categorization: " + " · ".join(f"{k}: {v}" for k, v in sorted(category_counts.items())))
        if st.button("Clear current session knowledge base", type="secondary"):
            st.session_state.chunks = []
            st.session_state.processed_docs = []
            st.session_state.file_hashes = set()
            st.session_state.last_answer = None
            st.session_state.last_results = []
            st.success("Cleared. Upload files again to build a fresh session index.")
            st.rerun()

elif page == "Explain a Topic":
    st.subheader("✨ Explain a topic from your sources")
    if not st.session_state.chunks:
        st.warning("Your knowledge base is empty. Go to **Upload & Process** and upload two or more academic documents first.")
        st.button("Go to Upload & Process →", type="primary", on_click=go_to, args=("Upload & Process",))
    else:
        docs_available = sorted({str(c.get("source", "Unknown")) for c in st.session_state.chunks})
        categories_available = sorted({str(c.get("category", "Other")) for c in st.session_state.chunks})
        st.caption(f"Indexed sources: {len(docs_available)} files · Categories detected: {', '.join(categories_available)}")
        with st.form("topic_form", clear_on_submit=False):
            question = st.text_area("What do you want to understand?", placeholder="Example: Explain CPU scheduling algorithms, compare FCFS and Round Robin, and use examples from my uploaded materials.", height=110)
            col1, col2, col3 = st.columns(3)
            with col1:
                category = st.selectbox("Source category", CATEGORIES, index=0)
            subject_options = sorted({
                c.get("subject", "Unassigned")
                for c in st.session_state.chunks
            })
            subject = st.selectbox(
                "Subject",
                ["All"] + subject_options,
                key="explain_subject",
            )

            chapter_options = sorted({
                c.get("chapter", "Unassigned")
                for c in st.session_state.chunks
                if subject == "All"
                or c.get("subject", "Unassigned") == subject
            })
            chapter = st.selectbox(
                "Chapter / Unit",
                ["All"] + chapter_options,
                key="explain_chapter",
            )
            with col2:
                language = st.selectbox("Answer language", ["English", "Hindi", "Hinglish"])
            with col3:
                level = st.selectbox("Explanation level", ["College beginner", "Exam revision", "Detailed"])
            top_k = st.slider("Evidence passages to compare", min_value=3, max_value=10, value=6)
            submitted = st.form_submit_button("Explain using my documents", type="primary", use_container_width=True)

        if submitted:
            if not question.strip():
                st.warning("Type a topic or question first.")
            else:
                with st.spinner("Searching your sources and preparing an explanation..."):
                    results = search_chunks(
                        st.session_state.chunks,
                        question,
                        top_k=top_k,
                        category=category,
                        subject=subject,
                        chapter=chapter,
                    )
                    if results:
                        generation = explain_topic(question, results, api_key=get_api_key(), language=language, level=level, model=get_gemini_model() or None)
                        st.session_state.last_question = question
                        st.session_state.last_results = results
                        st.session_state.last_answer = generation
                    else:
                        st.session_state.last_question = question
                        st.session_state.last_results = []
                        st.session_state.last_answer = None

        if st.session_state.last_question:
            if st.session_state.last_results and st.session_state.last_answer:
                res = st.session_state.last_results
                answer = st.session_state.last_answer
                source_count = len({r.get("source") for r in res})
                c1, c2, c3 = st.columns(3)
                c1.metric("Evidence passages", len(res))
                c2.metric("Source files used", source_count)
                c3.metric("Categories represented", len({r.get("category") for r in res}))
                st.markdown("### Explanation")
                st.caption(f"Mode: {answer['mode']}")
                if answer.get("notice"):
                    st.info(answer["notice"])
                with st.container(border=True):
                    st.markdown(answer["answer"])
                st.download_button(
                    "Download explanation (.md)",
                    data=f"# EduGen AI explanation\n\nQuestion: {st.session_state.last_question}\n\n{answer['answer']}\n",
                    file_name="edugen_topic_explanation.md",
                    mime="text/markdown",
                )
                st.markdown("### Sources and supporting evidence")
                st.caption("Source IDs [S1], [S2]… follow the order below. PDF page numbers and PPTX slide numbers are preserved; DOCX locations are approximate paragraph groups.")
                for idx, result in enumerate(res, 1):
                    render_source_card(result, idx)
                if source_count < 2 and len(docs_available) >= 2:
                    st.warning("Only one file matched this query. Try broader keywords or choose category ‘All’ to bring in additional sources.")
            elif not st.session_state.last_results:
                st.warning("No matching passages found. Try a shorter topic, switch category to All, or upload more relevant material.")

elif page == "Question Bank":
    st.subheader("📝 AI Question Bank Generator")
    st.write("Generate questions from your uploaded study materials.")

    if not st.session_state.chunks:
        st.warning("Pehle Upload & Process section mein study material upload aur process karo.")
        st.button(
            "Go to Upload & Process",
            type="primary",
            on_click=go_to,
            args=("Upload & Process",),
        )
    else:
        with st.form("question_bank_form"):
            topic = st.text_input(
                "Topic",
                placeholder="Example: CPU Scheduling Algorithms",
            )
            category = st.selectbox(
                "Source category",
                CATEGORIES,
                key="qb_category",
            )
            subject_options = sorted({
                c.get("subject", "Unassigned")
                for c in st.session_state.chunks
            })
            subject = st.selectbox(
                "Subject",
                ["All"] + subject_options,
                key="qb_subject",
            )

            chapter_options = sorted({
                c.get("chapter", "Unassigned")
                for c in st.session_state.chunks
                if subject == "All"
                or c.get("subject", "Unassigned") == subject
            })
            chapter = st.selectbox(
                "Chapter / Unit",
                ["All"] + chapter_options,
                key="qb_chapter",
            )
            col1, col2 = st.columns(2)
            with col1:
                mcq_count = st.number_input(
                    "Number of MCQs", min_value=0, max_value=20, value=5
                )
                short_count = st.number_input(
                    "Short questions", min_value=0, max_value=10, value=3
                )
            with col2:
                long_count = st.number_input(
                    "Long questions", min_value=0, max_value=5, value=2
                )
                difficulty = st.selectbox(
                    "Difficulty",
                    ["Easy", "Medium", "Hard", "Mixed"],
                    index=3,
                )

            generate = st.form_submit_button(
                "Generate Question Bank",
                type="primary",
                use_container_width=True,
            )

        if generate:
            if not topic.strip():
                st.warning("Pehle topic enter karo.")
            elif mcq_count + short_count + long_count == 0:
                st.warning("Kam se kam ek question select karo.")
            else:
                with st.spinner("Study material se questions generate ho rahe hain..."):
                    try:
                        results = search_chunks(
                            st.session_state.chunks,
                            topic,
                            top_k=10,
                            category=category,
                            subject=subject,
                            chapter=chapter,
                        )
                        if not results:
                            st.warning(
                                "Is topic ke matching passages nahi mile. "
                                "Topic ya source category change karke try karo."
                            )
                        else:
                            bank = generate_question_bank(
                                topic=topic,
                                results=results,
                                mcq_count=int(mcq_count),
                                short_count=int(short_count),
                                long_count=int(long_count),
                                difficulty=difficulty,
                                api_key=get_api_key(),
                                model=get_gemini_model() or None,
                            )
                            st.session_state["generated_question_bank"] = bank
                            st.session_state["question_bank_sources"] = results
                    except Exception as exc:
                        st.error(f"Question generation failed: {exc}")

        bank = st.session_state.get("generated_question_bank")
        if bank:
            st.markdown(f"### Questions: {bank.get('topic', '')}")
            st.caption(f"Difficulty: {bank.get('difficulty', difficulty if 'difficulty' in locals() else 'Mixed')}")

            st.markdown("#### MCQs")
            for i, q in enumerate(bank.get("mcqs", []), 1):
                with st.expander(f"MCQ {i}: {q.get('question', 'Question')}"):
                    options = q.get("options", {})
                    for label in ["A", "B", "C", "D"]:
                        if label in options:
                            st.write(f"**{label}.** {options[label]}")
                    st.markdown(f"**Correct answer:** {q.get('answer', 'Not provided')}")
                    st.write(q.get("explanation", ""))
                    st.caption(f"Source: {q.get('source', 'Not specified')}")

            st.markdown("#### Short-answer questions")
            for i, q in enumerate(bank.get("short_questions", []), 1):
                with st.expander(f"Short question {i}: {q.get('question', 'Question')}"):
                    st.write(q.get("answer", "Answer not provided"))
                    st.caption(f"Source: {q.get('source', 'Not specified')}")

            st.markdown("#### Long-answer questions")
            for i, q in enumerate(bank.get("long_questions", []), 1):
                with st.expander(f"Long question {i}: {q.get('question', 'Question')}"):
                    st.write(q.get("answer", "Answer not provided"))
                    st.caption(f"Source: {q.get('source', 'Not specified')}")

            st.download_button(
                "Download Question Bank (JSON)",
                data=__import__("json").dumps(
                    bank, ensure_ascii=False, indent=2
                ),
                file_name="edugen_question_bank.json",
                mime="application/json",
            )
            st.divider()
            render_quiz(st, bank)

elif page == "Content Synthesis":
    st.subheader("📚 AI Content Synthesis")
    st.write(
        "Combine information from your uploaded study materials "
        "into organized notes, comparisons, or revision summaries."
    )

    if not st.session_state.chunks:
        st.warning(
            "Pehle Upload & Process mein study material upload aur process karo."
        )
        st.button(
            "Go to Upload & Process",
            type="primary",
            on_click=go_to,
            args=("Upload & Process",),
        )
    else:
        with st.form("content_synthesis_form"):
            topic = st.text_input(
                "Topic",
                placeholder="Example: Software Requirements Engineering",
            )

            col1, col2 = st.columns(2)

            with col1:
                synthesis_category = st.selectbox(
                    "Source category",
                    CATEGORIES,
                    key="synthesis_category",
                )
                synthesis_subject = st.selectbox(
                    "Subject",
                    ["All"] + sorted({
                        c.get("subject", "Unassigned")
                        for c in st.session_state.chunks
                    }),
                    key="synthesis_subject",
                )

                synthesis_chapter = st.selectbox(
                    "Chapter / Unit",
                    ["All"] + sorted({
                        c.get("chapter", "Unassigned")
                        for c in st.session_state.chunks
                        if synthesis_subject == "All"
                        or c.get("subject", "Unassigned") == synthesis_subject
                    }),
                    key="synthesis_chapter",
                )

                synthesis_language = st.selectbox(
                    "Output language",
                    ["English", "Hindi", "Hinglish"],
                    key="synthesis_language",
                )

            with col2:
                format_type = st.selectbox(
                    "Output format",
                    ["Study Notes", "Comparison", "Quick Revision"],
                    key="synthesis_format",
                )

                synthesis_top_k = st.slider(
                    "Evidence passages to combine",
                    min_value=3,
                    max_value=10,
                    value=6,
                    key="synthesis_top_k",
                )

            synthesize_clicked = st.form_submit_button(
                "Generate Study Content",
                type="primary",
                use_container_width=True,
            )

        if synthesize_clicked:
            if not topic.strip():
                st.warning("Pehle topic enter karo.")
            elif not get_api_key():
                st.error(
                    "Gemini API key configured nahi hai. "
                    "Local .env ya Streamlit Cloud Secrets check karo."
                )
            else:
                with st.spinner(
                    "Uploaded documents ko compare karke content bana rahe hain..."
                ):
                    try:
                        results = search_chunks(
                            st.session_state.chunks,
                            topic,
                            top_k=synthesis_top_k,
                            category=synthesis_category,
                        )

                        if not results:
                            st.session_state["last_synthesis"] = None
                            st.warning(
                                "Matching passages nahi mile. "
                                "Topic ya source category change karke dekho."
                            )
                        else:
                            synthesis = synthesize_content(
                                topic=topic,
                                results=results,
                                api_key=get_api_key(),
                                language=synthesis_language,
                                format_type=format_type,
                                model=get_gemini_model() or None,
                            )

                            st.session_state["last_synthesis"] = synthesis
                            st.session_state["last_synthesis_results"] = results

                    except Exception as exc:
                        st.error(f"Content synthesis failed: {exc}")

        synthesis = st.session_state.get("last_synthesis")

        if synthesis:
            st.markdown(f"### {synthesis['topic']}")
            st.caption(
                f"Format: {synthesis['format']} | "
                f"Language: {synthesis['language']}"
            )

            with st.container(border=True):
                st.markdown(synthesis["content"])

            sources = synthesis.get("sources", [])
            st.markdown("#### Sources used")
            for source in sources:
                st.write(f"- {source}")

            st.download_button(
                "Download study content (.md)",
                data=(
                    f"# {synthesis['topic']}\n\n"
                    f"Format: {synthesis['format']}\n\n"
                    f"{synthesis['content']}\n"
                ),
                file_name="edugen_synthesized_notes.md",
                mime="text/markdown",
            )

elif page == "Document Library":
    st.subheader("🗂️ Document library")

    if not st.session_state.processed_docs:
        st.info("No documents processed in this session yet.")
        st.button(
            "Upload documents →",
            type="primary",
            on_click=go_to,
            args=("Upload & Process",),
        )
    else:
        docs = st.session_state.processed_docs

        subjects = sorted({
            d.get("subject", "Unassigned") or "Unassigned"
            for d in docs
        })
        selected_subject = st.selectbox(
            "Filter by Subject",
            ["All"] + subjects,
        )

        filtered_docs = docs
        if selected_subject != "All":
            filtered_docs = [
                d for d in docs
                if (d.get("subject", "Unassigned") or "Unassigned")
                == selected_subject
            ]

        chapters = sorted({
            d.get("chapter", "Unassigned") or "Unassigned"
            for d in filtered_docs
        })
        selected_chapter = st.selectbox(
            "Filter by Chapter / Unit",
            ["All"] + chapters,
        )

        if selected_chapter != "All":
            filtered_docs = [
                d for d in filtered_docs
                if (d.get("chapter", "Unassigned") or "Unassigned")
                == selected_chapter
            ]

        st.caption(f"Showing {len(filtered_docs)} of {len(docs)} documents")
        st.dataframe(
            filtered_docs,
            use_container_width=True,
            hide_index=True,
        )

        categories = Counter(
            d.get("category", "Other") for d in filtered_docs
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Category breakdown")
            if categories:
                st.bar_chart({
                    "Category": list(categories.keys()),
                    "Files": list(categories.values()),
                }, x="Category", y="Files")
            else:
                st.info("No documents match these filters.")

        with col2:
            st.markdown("#### Sources represented in index")
            selected_names = {d["name"] for d in filtered_docs}
            source_counts = Counter(
                c.get("source", "Unknown")
                for c in st.session_state.chunks
                if c.get("source") in selected_names
            )
            st.dataframe(
                [
                    {"Source": name, "Chunks": count}
                    for name, count in source_counts.items()
                ],
                hide_index=True,
                use_container_width=True,
            )

st.divider()
st.markdown("<div class='small-muted'>EduGen AI · Track A · Academic sources first, answers with citations.</div>", unsafe_allow_html=True)

