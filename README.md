# Multimodal Summarizer

## 🚀 Run Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

- Backend runs on http://localhost:8000
- Frontend runs on http://localhost:3000

## 🐳 Run with Docker

### Backend
```bash
cd backend
docker build -t summarizer-backend .
docker run -p 8000:8000 --env-file .env summarizer-backend
```

### Frontend
```bash
cd frontend
docker build -t summarizer-frontend .
docker run -p 3000:3000 summarizer-frontend
```

---
