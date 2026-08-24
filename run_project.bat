@echo off
echo ===================================================
echo Starting OneSpot.AI (Information Retrieval Project)
echo ===================================================

echo [1/3] Starting Task 1 Backend (Vertical Search) on Port 5001...
start cmd /k "call .venv\Scripts\activate.bat && cd task1_vertical_search\backend && python run.py"

echo [2/3] Starting Task 2 Backend (Document Clustering) on Port 5002...
start cmd /k "call .venv\Scripts\activate.bat && cd task2_document_clustering\backend && python run.py"

echo [3/3] Starting Unified Frontend on Port 5003...
start cmd /k "call .venv\Scripts\activate.bat && cd unified_frontend && python app.py"

echo.
echo All services are booting up!
echo Waiting a few seconds for the backends to start...
timeout /t 4 /nobreak > nul

echo Opening the application in your web browser...
start http://localhost:5003

echo Done! You can close this window. The 3 server windows will remain open.
