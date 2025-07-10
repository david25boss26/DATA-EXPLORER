@echo off
echo 🚀 Setting up Data Explorer and LLM Summary Dashboard
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

echo ✅ Python and Node.js are installed

REM Create necessary directories
echo 📁 Creating directories...
if not exist "backend\data" mkdir backend\data
if not exist "backend\uploads" mkdir backend\uploads
if not exist "backend\models" mkdir backend\models

REM Setup backend
echo 🐍 Setting up Python backend...
cd backend

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Copy environment file
if not exist ".env" (
    copy env.example .env
    echo 📝 Created .env file. Please edit it with your configuration.
)

cd ..

REM Setup frontend
echo ⚛️ Setting up React frontend...
cd frontend

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

cd ..

echo.
echo 🎉 Setup completed successfully!
echo.
echo Next steps:
echo 1. Edit backend\.env with your LLM configuration
echo 2. Start the backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo 3. Start the frontend: cd frontend ^&^& npm start
echo.
echo The application will be available at:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo.
echo For LLM setup options, see the README.md file.
pause 