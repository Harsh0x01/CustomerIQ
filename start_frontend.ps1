# CustomerIQ — Start Frontend
# Usage: .\start_frontend.ps1

Write-Host "🧠 Starting CustomerIQ Frontend..." -ForegroundColor Cyan
Write-Host "Dashboard will open at: http://localhost:8501" -ForegroundColor Green

Set-Location $PSScriptRoot
& .\.venv\Scripts\streamlit.exe run frontend/app.py
