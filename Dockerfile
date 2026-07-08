# ── Stage 1: build deps ──────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools needed by some wheels (e.g. chromadb)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy source code
COPY . .

# Create persistent data directories
# Create persistent data directories and symlink uploaded_dbs into volume
RUN mkdir -p /data/chroma_db /data/uploaded_dbs && \
    ln -s /data/uploaded_dbs /app/uploaded_dbs

# Expose ports: 8000 (FastAPI) and 8501 (Streamlit)
EXPOSE 8000 8501

# Environment defaults (overridden at runtime via --env-file or -e)
ENV DATABASE_URL=sqlite:////data/text2sql.db \
    CHROMA_PERSIST_DIR=/data/chroma_db \
    DEBUG=false \
    SAFE_MODE=true \
    PORT=8501

# Start both services via start.sh
RUN chmod +x start.sh
CMD ["bash", "start.sh"]
