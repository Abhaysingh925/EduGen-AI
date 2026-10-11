# GitHub + Streamlit Community Cloud deployment

## A. Prepare the project on your computer

1. Extract the ZIP into a clean folder such as `C:\Users\vikas\EduGen-AI`.
2. Open PowerShell in that folder.
3. Create and activate a virtual environment, then install `requirements.txt` using the commands in `README.md`.
4. Run `python -m streamlit run app.py` and test the sample documents. Fix local errors before deploying.
5. Confirm `.gitignore` excludes `venv/`, `.env`, `__pycache__/`, and `.streamlit/secrets.toml`.

## B. Create the GitHub repository

1. Open <https://github.com/new> and create a repository named `EduGen-AI`.
2. For the first push, leave the options to add a README, `.gitignore`, or license unchecked, because these files already exist in the project folder.
3. In PowerShell, from the project root:

   ```powershell
   git --version
   git init
   git add .
   git status
   git commit -m "Build EduGen AI Track A MVP"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/EduGen-AI.git
   git push -u origin main
   ```

4. Replace `YOUR_USERNAME` with your GitHub username. If Git is not installed, install Git for Windows first. If identity is missing, set it with `git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"`, then repeat the commit.
5. Never upload API keys, `.env`, virtual environments, private study files, or real student records.

### If the two-member repository belongs to a teammate

- Safest route: ask the teammate to invite your GitHub username under **Repository → Settings → Collaborators**. Then you can contribute a branch/PR or, with permission, push to the shared repository.
- If access is not granted, make a separate `EduGen-AI` repository under your account and deploy that. You can later open a pull request into the teammate's public repo, or copy/merge your files after the owner grants access. Do not overwrite their main branch without coordination.

## C. Deploy on Streamlit Community Cloud

1. Open <https://share.streamlit.io/> and sign in with GitHub.
2. Choose **Create app**.
3. Select repository `YOUR_USERNAME/EduGen-AI`, branch `main`, and entrypoint `app.py`.
4. In **Advanced settings**, select **Python 3.12**. The project requirements install FAISS on Linux with Python versions below 3.14. On your Windows laptop with Python 3.14, FAISS is skipped and the app uses its scikit-learn cosine-similarity fallback. Streamlit Community Cloud lets you choose the Python version during deployment.
5. Optional: in **Secrets**, paste:

   ```toml
   GEMINI_API_KEY = "YOUR_KEY_HERE"
   GEMINI_MODEL = "gemini-3.5-flash-lite"
   ```

6. Click **Deploy**. When the app starts, test the same five sample documents from the live website.
7. Copy the published `*.streamlit.app` URL for your teacher and teammates.

If the app fails to build, open **Manage app → Logs** and fix the first dependency/import error shown. Do not guess; use the error message.

## D. After publishing

- Check upload, processing, category detection, topic retrieval, source locations, and Gemini response.
- Keep an API-key-enabled demo private or share only with the intended audience if the platform/account settings allow it. If a public app uses your own API key, other visitors may consume its quota.
- Streamlit session state is temporary; users normally need to re-upload files in their own session. Persistent shared storage is outside this Week 1–2 milestone.
