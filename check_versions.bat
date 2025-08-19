@echo off
echo ==== Python Version ==== > version_log.txt
python --version >> version_log.txt 2>&1

echo. >> version_log.txt
echo ==== Backend Python Packages ==== >> version_log.txt
pip show fastapi uvicorn ultralytics opencv-python numpy python-multipart >> version_log.txt 2>&1

echo. >> version_log.txt
echo ==== Installed Python Packages (Freeze) ==== >> version_log.txt
pip freeze >> version_log.txt 2>&1

echo. >> version_log.txt
echo ==== Node.js & NPM Versions ==== >> version_log.txt
node -v >> version_log.txt 2>&1
npm -v >> version_log.txt 2>&1

echo. >> version_log.txt
echo ==== React + Frontend Packages ==== >> version_log.txt
cd frontend
npm list --depth=0 >> ..\version_log.txt 2>&1
cd ..

echo. >> version_log.txt
echo ==== Docker Versions ==== >> version_log.txt
docker --version >> version_log.txt 2>&1
docker compose version >> version_log.txt 2>&1

echo.
echo ✅ All versions written to version_log.txt