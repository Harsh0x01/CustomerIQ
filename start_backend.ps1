# CustomerIQ — Start Backend
# Usage: .\start_backend.ps1

Write-Host "🚀 Starting CustomerIQ Backend..." -ForegroundColor Cyan
Write-Host "API docs will be available at: http://localhost:8000/docs" -ForegroundColor Green

Set-Location $PSScriptRoot
& .\.venv\Scripts\uvicorn.exe backend.main:app --reload --host 0.0.0.0 --port 8000
