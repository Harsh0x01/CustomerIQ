# CustomerIQ — Unified Startup Script
# This script launches all necessary services in separate terminal windows.

Write-Host "🚀 Launching CustomerIQ Platform..." -ForegroundColor Cyan

# 1. Start Backend (FastAPI)
Write-Host "  -> Starting Backend on http://localhost:8000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location $PSScriptRoot; & .\.venv\Scripts\uvicorn.exe backend.main:app --reload --host 0.0.0.0 --port 8000"

# 2. Start Celery Worker
Write-Host "  -> Starting Celery Worker" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location $PSScriptRoot; & .\.venv\Scripts\celery.exe -A backend.tasks worker --loglevel=info -P solo"

# 3. Start Frontend (Streamlit)
Write-Host "  -> Starting Frontend on http://localhost:8501" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location $PSScriptRoot; & .\.venv\Scripts\streamlit.exe run frontend/app.py"

Write-Host "✅ All services initiated. Check the new windows for logs." -ForegroundColor Green
