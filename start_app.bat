@echo off
echo ========================================
echo Wasserstoff-Kostenrechner App
echo ========================================
echo.

REM Versuche verschiedene Python-Befehle
where py >nul 2>&1
if %errorlevel% == 0 (
    echo Python gefunden! Starte App...
    echo.
    py wasserstoff_app.py
    goto :end
)

where python >nul 2>&1
if %errorlevel% == 0 (
    echo Python gefunden! Starte App...
    echo.
    python wasserstoff_app.py
    goto :end
)

where python3 >nul 2>&1
if %errorlevel% == 0 (
    echo Python gefunden! Starte App...
    echo.
    python3 wasserstoff_app.py
    goto :end
)

echo.
echo FEHLER: Python wurde nicht gefunden!
echo.
echo Bitte installieren Sie Python von:
echo https://www.python.org/downloads/
echo.
echo Oder verwenden Sie den Python Launcher (py):
echo py wasserstoff_app.py
echo.
pause
:end
