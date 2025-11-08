@echo off
title InternHub API Server
echo ================================
echo Starting InternHub API Server
echo ================================
echo.

:: Kill any existing processes on port 8000
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8000 ^| findstr LISTENING') do (
    echo Warning: Port 8000 in use by process %%a, killing it...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

:: Set environment variables
set DATABASE_URL=postgresql+psycopg://hub:hubpass@localhost:5433/hubdb_v2
set PYTHONPATH=.

:: Activate virtual environment and start server
echo Activating virtual environment...
call .venv\Scripts\activate
echo Starting server on http://localhost:8000
echo Press CTRL+C to stop
echo.
python -c "import asyncio, uvicorn; asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()); uvicorn.run('app.main:app', host='0.0.0.0', port=8000, proxy_headers=True, forwarded_allow_ips='*')"

