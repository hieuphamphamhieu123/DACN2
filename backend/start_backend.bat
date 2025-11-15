@echo off
echo ================================================
echo Starting Social Network Backend API
echo ================================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8080
echo API Documentation: http://localhost:8080/docs
echo.

python -m uvicorn app.main:app --reload --port 8080

pause
