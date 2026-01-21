@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting web server...
echo Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
