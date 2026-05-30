# Indian Movie Charades — single-service deploy (FastAPI serves API + cinema UI)
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

WORKDIR /app/backend
EXPOSE 8000
# Hosts (Render, Fly, HF Spaces) inject $PORT; default 8000 locally.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
