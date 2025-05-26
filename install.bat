@echo off
REM ================================================================================
REM Watkibot Law Assistant - Simplified Installation Script
REM ================================================================================

echo ========================================================================
echo Watkibot Law Assistant - Simplified Installation Script
echo ========================================================================
echo.

REM Create installation directory
set "INSTALL_DIR=C:\WatkibotLawAssistant"
echo Creating installation directory: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy application files
echo Copying application files...
xcopy /E /I /Y "%~dp0backend" "%INSTALL_DIR%\backend"
xcopy /E /I /Y "%~dp0frontend" "%INSTALL_DIR%\frontend"

REM Setup backend
echo Setting up backend...
cd "%INSTALL_DIR%\backend"

REM Create Python virtual environment
echo Creating Python virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment with venv.
    echo Continuing without virtual environment...
    goto :skip_venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

:skip_venv

REM Setup frontend
echo Setting up frontend...
cd "%INSTALL_DIR%\frontend"

REM Install Node.js dependencies
echo Installing Node.js dependencies...
call npm install

REM Create startup scripts
echo Creating startup scripts...
cd "%INSTALL_DIR%"

REM Create backend startup script
echo @echo off > start_backend.bat
echo cd "%INSTALL_DIR%\backend" >> start_backend.bat
echo if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat >> start_backend.bat
echo python -m app.main >> start_backend.bat
echo pause >> start_backend.bat

REM Create frontend startup script
echo @echo off > start_frontend.bat
echo cd "%INSTALL_DIR%\frontend" >> start_frontend.bat
echo npm start >> start_frontend.bat
echo pause >> start_frontend.bat

REM Create combined startup script
echo @echo off > start_watkibot.bat
echo echo Starting Watkibot Law Assistant... >> start_watkibot.bat
echo start "Watkibot Backend" "%INSTALL_DIR%\start_backend.bat" >> start_watkibot.bat
echo start "Watkibot Frontend" "%INSTALL_DIR%\start_frontend.bat" >> start_watkibot.bat
echo echo Watkibot Law Assistant is starting up. >> start_watkibot.bat
echo echo Please wait a moment, then navigate to http://localhost:3000 in your web browser. >> start_watkibot.bat
echo pause >> start_watkibot.bat

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Watkibot Law Assistant.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\start_watkibot.bat'; $Shortcut.Save()"

echo.
echo ========================================================================
echo Installation completed!
echo.
echo Watkibot Law Assistant has been installed to: %INSTALL_DIR%
echo A shortcut has been created on your desktop.
echo.
echo To start the application:
echo 1. Double-click the 'Watkibot Law Assistant' shortcut on your desktop
echo 2. Navigate to http://localhost:3000 in your web browser
echo.
echo If you encounter any issues, you can start the components separately:
echo 1. Run %INSTALL_DIR%\start_backend.bat
echo 2. Run %INSTALL_DIR%\start_frontend.bat in a separate window
echo.
echo ========================================================================

echo.
echo Press any key to exit...
pause > nul
