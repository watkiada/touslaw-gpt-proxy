@echo off
echo This is a manual installation guide for Watkibot Law Assistant
echo.
echo Step 1: Setting up the backend
echo ------------------------------
echo.
pause

cd /d %~dp0
cd backend

echo Creating Python virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment with venv.
    echo Trying with virtualenv...
    pip install virtualenv
    virtualenv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment with virtualenv.
        echo Continuing without virtual environment...
    )
)

echo.
echo Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment activation failed, continuing without it...
)

echo.
echo Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies. Please check the error message above.
    pause
)

echo.
echo Step 2: Setting up the frontend
echo ------------------------------
echo.
pause

cd /d %~dp0
cd frontend

echo Installing Node.js dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install Node.js dependencies. Please check the error message above.
    pause
)

echo.
echo Step 3: Creating startup scripts
echo ------------------------------
echo.
pause

cd /d %~dp0

echo Creating backend startup script...
echo @echo off > start_backend.bat
echo cd /d "%%~dp0backend" >> start_backend.bat
echo if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat >> start_backend.bat
echo python -m app.main >> start_backend.bat
echo pause >> start_backend.bat

echo Creating frontend startup script...
echo @echo off > start_frontend.bat
echo cd /d "%%~dp0frontend" >> start_frontend.bat
echo npm start >> start_frontend.bat
echo pause >> start_frontend.bat

echo.
echo Installation completed!
echo.
echo To start the application:
echo 1. Run start_backend.bat
echo 2. Run start_frontend.bat in a separate window
echo 3. Navigate to http://localhost:3000 in your web browser
echo.

pause
