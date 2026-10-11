# 2-minute demo script — EduGen-AI Track A

## Before recording

1. Start the app and have the Gemini API key configured if possible.
2. On Dashboard, download the five sample files, then upload all five: textbook PDF, lecture notes DOCX, question bank DOCX, lab manual DOCX, and lab slides PPTX.
3. Confirm the document library shows five files with different categories.
4. Open Explain a Topic, choose category **All**, language **English**, level **Exam revision**.

## Timed run (about 2 minutes)

**0:00–0:15 — Problem and home screen**

“Students often have the same topic spread across lecture notes, textbooks, question banks and lab materials. EduGen-AI brings those formats into one academic workspace.”

**0:15–0:40 — Multi-format upload**

Show Upload & Process. Explain that the app accepts PDF, DOCX and PPTX, extracts their text, cleans and chunks it, and automatically categorizes each file as Notes, Textbook, Questions, Labs or Other.

**0:40–1:00 — Retrieval**

Show Document Library and point to the files, categories and chunk counts. Explain that lightweight TF-IDF vectors are indexed using FAISS, and the question is matched to relevant evidence chunks.

**1:00–1:35 — Comprehensive topic explanation**

Ask: “Explain CPU scheduling. Compare FCFS and Round Robin, and give exam revision points.” Keep category All. Show the answer and source list. Point out that source IDs and page/slide/section metadata make the answer auditable across several uploaded files.

**1:35–1:50 — Trust and limitations**

Show the source evidence. Say: “When a Gemini API key is configured, the language model produces a structured answer grounded in the retrieved excerpts. Without a key, the app clearly switches to source-excerpt mode rather than claiming an AI-generated answer.”

**1:50–2:00 — Milestone**

“The Week 1–2 quick win is a working multi-document academic assistant with processing, categorization, topic retrieval, source references, a Streamlit interface and a shareable deployment.”

## Recording

Use Windows Snipping Tool screen recording or PowerPoint screen recording. Keep the cursor steady, enlarge the browser to readable size, and show a live question + result rather than only scrolling through code.
