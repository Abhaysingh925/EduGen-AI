# Track A checklist — implementation status

| Checklist item | Status in this package | What is still manual |
|---|---|---|
| Create GitHub repo with academic assistant structure | Project structure, README, ignore rules, sample docs and Git deployment guide included | Create repository in your GitHub account and push code |
| Set up Python, LangChain, Streamlit, PyPDF2, FAISS | Dependencies declared in `requirements.txt`; Python version guidance included. On Windows/Python 3.14 the app uses the scikit-learn fallback; FAISS is enabled for Linux/Python <3.14 (use Python 3.12 on Streamlit Cloud). | Install dependencies in your local environment |
| Multi-format document processing (PDF, DOCX, PPTX) | Implemented in `processors/` and `document_pipeline.py` | Test with the actual course files; scanned PDFs need OCR |
| Content categorization (notes, textbook, questions, labs) | Implemented by `utils/categorizer.py` and displayed in UI | Review heuristic labels if a filename is ambiguous |
| Topic-based retrieval | TF-IDF vectors + FAISS similarity search; cosine fallback for local troubleshooting | Test the target course topics; neural semantic embeddings are a later enhancement |
| Streamlit UI for multi-document upload and topic queries | Implemented in `app.py` | Run locally and confirm it works on your laptop |
| Deploy basic version on Streamlit Cloud | Full step-by-step guide is included | Push to GitHub, select the repo/entrypoint and deploy; this package has not been deployed to your account |
| Record a 2-minute demo | Timed narration and demo steps included in `DEMO_SCRIPT.md` | Screen-record the running app after local/cloud testing |
| Milestone: explain topics using multiple source types | App retrieves from several documents/categories and displays source passages; Gemini can generate a structured answer citing sources | Add a valid Gemini API key to enable generated explanations; without key, app clearly uses extractive source-based mode |

## Acceptance test

Upload the five sample files, ask `Explain CPU scheduling. Compare FCFS and Round Robin, and give exam revision points.` with category `All`, and check for results from multiple files and source locations. Then repeat with two of your real academic documents.
