#!/bin/bash

echo "==== Python Version ====" > version_log.txt
python --version >> version_log.txt 2>&1

echo -e "\n==== Backend Python Packages ====" >> version_log.txt
pip show fastapi uvicorn ultralytics opencv-python numpy python-multipart >> version_log.txt 2>&1

echo -e "\n==== Installed Python Packages (Freeze) ====" >> version_log.txt
pip freeze >> version_log.txt 2>&1

echo -e "\n==== Node.js & NPM Versions ====" >> version_log.txt
node -v >> version_log.txt 2>&1
npm -v >> version_log.txt 2>&1

echo -e "\n==== React + Frontend Packages ====" >> version_log.txt
cd frontend || exit
npm list --depth=0 >> ../version_log.txt 2>&1
cd .. || exit

echo -e "\n==== Docker Versions ====" >> version_log.txt
docker --version >> version_log.txt 2>&1
docker compose version >> version_log.txt 2>&1

echo -e "\n==== Version collection complete. Output saved to version_log.txt ===="
