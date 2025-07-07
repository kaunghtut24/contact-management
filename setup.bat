@echo off
echo Setting up Contact Management System...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed. Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed. Please install Node.js 16+ and try again.
    pause
    exit /b 1
)

echo Setting up backend...

REM Create virtual environment
cd backend
if not exist "venv" (
    python -m venv venv
    echo Created Python virtual environment
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
echo Installed Python dependencies

REM Create necessary directories
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs
echo Created upload and log directories

REM Copy environment file
if not exist ".env" (
    copy .env.example .env
    echo Created .env file from template
    echo WARNING: Please update the .env file with your database credentials
)

cd ..

echo Setting up frontend...

REM Install Node.js dependencies
cd frontend
npm install
echo Installed Node.js dependencies

cd ..

echo Setup completed successfully!
echo.
echo Next steps:
echo 1. Update backend\.env with your PostgreSQL database credentials
echo 2. Create the PostgreSQL database 'contact_db'
echo 3. Start the backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo 4. Start the frontend: cd frontend ^&^& npm run dev
echo.
echo Or use Docker Compose: docker-compose up -d
echo.
echo Access the application at: http://localhost:5173
echo API documentation at: http://localhost:8000/docs

pause
