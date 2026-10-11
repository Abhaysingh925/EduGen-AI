# EduGen-AI — pehle ye steps follow karo (Hindi/Hinglish)

## 1. ZIP extract karo

1. `EduGen-AI-TrackA.zip` download karo.
2. ZIP par right-click → **Extract All**.
3. Extracted `EduGen-AI-TrackA` folder ko, example ke liye, `C:\Users\vikas\EduGen-AI-TrackA` par rakho.
4. Apne purane `Member3_App` ko delete mat karna. Naye folder mein clean project test karna safer hai.

## 2. PowerShell mein project folder kholo

```powershell
cd "$env:USERPROFILE\EduGen-AI-TrackA"
```

Agar folder kahin aur extract kiya hai, command mein uska actual path likho.

## 3. Virtual environment aur packages

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --timeout 120 --retries 10
```

Agar activation execution-policy error de, sirf isi PowerShell window ke liye ye command chalao, phir activate dobara karo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Agar download timeout aaye, same install command dobara try karo, ya stable Wi-Fi/hotspot se try karo. Installer ka last error save karke rakho.

## 4. App chalao

```powershell
python -m streamlit run app.py
```

Browser khulna chahiye. Na khule toh terminal ka `Local URL` browser mein open karo.

## 5. End-to-end test

1. Dashboard par sample files download karo.
2. **Upload & Process** page kholo.
3. Sample PDF, Notes DOCX, Question Bank DOCX, Lab Manual DOCX, aur Lab Slides PPTX sab upload karo.
4. **Process & index files** dabao.
5. **Explain a Topic** par jaakar category `All` rakho.
6. Ye query poochho: `Explain CPU scheduling. Compare FCFS and Round Robin, and give exam revision points.`
7. Check karo ki explanation ke neeche kai source files, categories, page/slide/section references dikh rahe hain.

Gemini API key configure nahi hai toh app source excerpts se explanation dega. Gemini se generated explanation ke liye Google AI Studio key ko local environment variable ya Streamlit Cloud Secrets mein configure karo. Key ko code ya GitHub par mat likho.

## 6. GitHub aur Streamlit Cloud

Exact commands aur teammate ki repository mein contribution vs apni repository choose karne ke steps `DEPLOYMENT_GUIDE.md` mein hain. Pehle local test pass karo, phir repository push aur hosting karo.
