# EduGen-AI — Track A (Week 1–2 Foundation & Quick Win)

EduGen-AI is a multi-document academic assistant prototype. Upload PDF, DOCX, and PPTX study material, automatically categorize each document, retrieve topic-relevant passages across files, and view an explanation with source/page/slide references.

## What is implemented

- **Multi-format ingestion:** PDF via PyPDF2, Word via python-docx, PowerPoint via python-pptx.
- **Cleaning and chunking:** normalizes extracted text, removes repeated short headers/footers where possible, and adds overlap between chunks.
- **Automatic categories:** Notes, Textbook, Questions, Labs, or Other based on filenames and a small text sample. Categories are heuristic, so review them in the UI.
- **Topic-based retrieval:** TF-IDF vectors ranked through FAISS inner-product similarity search. This deliberately lightweight retrieval avoids downloading a multi-hundred-megabyte embedding model and is suitable for a first milestone. If FAISS is unavailable locally, a scikit-learn cosine-similarity fallback is used.
- **LangChain:** retrieved evidence is represented as LangChain Core `Document` objects and `PromptTemplate` formats the grounded generation prompt.
- **Explanation:** with `GEMINI_API_KEY`, Google Gemini generates a structured answer constrained to retrieved excerpts and asked to cite `[S1]`, `[S2]`, etc. Without a key, the app provides an explicitly labelled extractive explanation from source passages.
- **Evidence panel:** shows the matched source, category, PDF page / PPT slide / approximate DOCX paragraph group, and similarity score.
- **Multi-document Streamlit UI:** dashboard, uploader, topic explainer, document library, category filters, downloads, and Track A checklist.
- **Sample files:** five small synthetic OS documents are included so the end-to-end demo can be tried without finding study files.

## Important limitations

- This is a Week 1–2 MVP, not production-grade RAG. TF-IDF is lexical vectorization rather than a neural semantic embedding. A later phase can replace it with Sentence Transformers or an embedding API while keeping the same chunk metadata contract.
- Scanned/image-only PDF pages do not contain extractable text. OCR is not included in this milestone.
- `python-docx` does not expose stable rendered page boundaries; DOCX locations are approximate paragraph groups, not true page numbers.
- Uploaded documents and processed chunks live in the current Streamlit session. They are not a persistent multi-user database; after session loss, upload the documents again.
- Gemini generation requires an API key. Never commit an API key to GitHub. A public app using your API key can incur usage, so use a limited/test key and monitor it.

## Project structure

```text
EduGen-AI/
├── app.py
├── document_pipeline.py
├── retrieval.py
├── prompts.py
├── llm.py
├── requirements.txt
├── .env.example
├── .gitignore
├── processors/          # PDF/DOCX/PPTX extraction
├── utils/               # cleaner, categorizer, chunker
├── sample_docs/         # demo documents (synthetic)
├── tests/
├── DEPLOYMENT_GUIDE.md
└── DEMO_SCRIPT.md
```

## Run locally (Windows PowerShell)

Your laptop currently has Python 3.14 installed, so you can run the project locally with that version. On Windows/Python 3.14, FAISS is intentionally skipped and EduGen-AI uses its scikit-learn cosine-similarity fallback. For Streamlit Community Cloud, choose Python 3.12 in Advanced settings so the Linux FAISS package can be installed; always inspect deployment logs if a dependency fails.

```powershell
cd C:\path\to\EduGen-AI
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --timeout 120 --retries 10
python -m streamlit run app.py
```

If the PowerShell execution policy blocks activation, run this for the current terminal only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

For a quick local fallback without Gemini, simply leave `GEMINI_API_KEY` unset. The app still extracts, indexes, retrieves, and shows source excerpts. For generated topic explanations, set `GEMINI_API_KEY` in the environment or configure Streamlit Secrets as shown below.

## Gemini key (optional but recommended for the milestone demo)

1. Create a key at <https://aistudio.google.com/apikey>.
2. For local use, copy `.env.example` to `.env`, paste the key after `GEMINI_API_KEY=`. The app loads `.env` automatically; alternatively set a PowerShell environment variable for the current terminal:

   ```powershell
   $env:GEMINI_API_KEY="YOUR_KEY_HERE"
   python -m streamlit run app.py
   ```

3. For Streamlit Cloud, use the app's **Advanced settings → Secrets** field and add:

   ```toml
   GEMINI_API_KEY = "YOUR_KEY_HERE"
   GEMINI_MODEL = "gemini-3.5-flash-lite"
   ```

The exact model name is configurable in `GEMINI_MODEL`. Confirm currently available model IDs in the official Gemini API model list if this model is unavailable.

## Basic validation checklist

1. Upload the sample PDF, Notes DOCX, Question Bank DOCX, Lab Manual DOCX, and Lab Slides PPTX.
2. Confirm all five are processed and categorized as Textbook, Notes, Questions, and Labs.
3. Open **Explain a Topic**, keep category **All**, and ask: `Explain CPU scheduling. Compare FCFS and Round Robin, and give exam revision points.`
4. Confirm results contain multiple source files and correct PDF page / PPT slide / DOCX section labels.
5. With the Gemini key configured, confirm a generated explanation includes references like `[S1]`. Without it, confirm the app explicitly labels extractive mode rather than claiming generated AI output.
6. Test one additional user PDF or slide deck; do not rely only on the bundled samples.

See `DEPLOYMENT_GUIDE.md` for GitHub and Streamlit Cloud steps and `DEMO_SCRIPT.md` for a timed presentation outline.
