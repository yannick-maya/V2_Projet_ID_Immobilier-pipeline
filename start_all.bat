@echo off
REM Script de demarrage rapide - ID Immobilier
REM Lance l'API, frontend et admin simultanement

echo.
echo ====================================================
echo  DEMARRAGE RAPIDE - ID IMMOBILIER
echo ====================================================
echo.
echo Ce script va lancer:
echo  1. API FastAPI (port 8000)
echo  2. Frontend Utilisateur (port 3000)
echo  3. Admin Interface (port 3001)
echo.
echo Assurez-vous que:
echo  - MongoDB Atlas est accessible
echo  - Python 3.11+ est installe
echo  - Node.js et npm sont installes
echo.
pause

cd /d D:\PROJECTS\Projet_Immobilier\id_immobilier

REM Lancer l'API dans une nouvelle fenetre
start "API (8000)" cmd /k python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

REM Attendre un peu avant de lancer les autres
timeout /t 3

REM Lancer Frontend dans une nouvelle fenetre
start "Frontend (3000)" cmd /k cd frontend && npm start

REM Attendre un peu
timeout /t 2

REM Lancer Admin dans une nouvelle fenetre
start "Admin (3001)" cmd /k cd admin && set REACT_APP_API_URL=http://localhost:8000 && npm start

echo.
echo ====================================================
echo DEMARRAGE EN COURS...
echo ====================================================
echo.
echo Utilisateurs de test:
echo  - USER: yannickmadjiadoum23@gmail.com (admin)
echo  - USER: nickson@gmail.com (user)
echo.
echo Acces:
echo  - Frontend User: http://localhost:3000
echo  - Admin Panel: http://localhost:3001
echo  - API Docs: http://localhost:8000/docs
echo.
echo Appuyez sur une touche pour terminer...
pause
