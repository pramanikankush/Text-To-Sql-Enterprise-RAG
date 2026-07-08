#!/bin/bash
# Start FastAPI backend in the background on local port 8000
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait for backend to be ready using python (so we don't depend on curl)
echo "Waiting for backend to start..."
python -c "
import time, urllib.request
for _ in range(30):
    try:
        if urllib.request.urlopen('http://127.0.0.1:8000/health').getcode() == 200:
            break
    except Exception:
        pass
    time.sleep(1)
"
echo "Backend is ready!"

# Start Streamlit frontend in the foreground on the port assigned by Railway
python -m streamlit run frontend/streamlit_app.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.headless true

