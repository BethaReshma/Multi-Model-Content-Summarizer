import os
import fitz  # PyMuPDF
from docx import Document
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import zipfile
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Summarizer MVP")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API key safely
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("❌ OPENAI_API_KEY not set. Add it to .env or export it.")

client = OpenAI(api_key=api_key)

# ---------- File Text Extraction ----------
def extract_text(file_path: str, ext: str) -> str:
    if ext == "pdf":
        text = []
        doc = fitz.open(file_path)
        for page in doc:
            text.append(page.get_text())
        return "\n".join(text)

    elif ext == "docx":
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    elif ext == "txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext == "zip":
        combined = []
        with zipfile.ZipFile(file_path, "r") as z:
            for name in z.namelist():
                inner_ext = name.split(".")[-1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{inner_ext}") as tmp:
                    tmp.write(z.read(name))
                    tmp.flush()
                    try:
                        combined.append(extract_text(tmp.name, inner_ext))
                    except Exception:
                        combined.append(f"[Could not extract {name}]")
        return "\n".join(combined)

    else:
        raise ValueError("Unsupported file type")

# ---------- API Endpoint ----------
@app.post("/summarize")
async def summarize(file: UploadFile = File(...), prompt: str = Form("")):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ("pdf", "docx", "txt", "zip"):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, TXT, ZIP supported")

    # Save uploaded file temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Extract text
    try:
        content = extract_text(temp_path, ext)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    # Summarize using OpenAI
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful summarizer."},
                {"role": "user", "content": f"{prompt}\n\nContent:\n{content[:5000]}"},
            ],
        )
        summary = completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")

    return {"summary": summary}

@app.get("/health")
async def health():
    return {"status": "ok"}
