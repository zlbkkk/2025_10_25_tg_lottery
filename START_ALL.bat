@echo off
chcp 65001 >nul
title Telegram Lottery Bot System - Quick Start
cls

echo ========================================
echo   Telegram Lottery Bot System
echo ========================================
echo.
echo Starting all services...
echo.

echo [1/3] Starting Backend Server...
start "Backend Server" cmd /k "cd /d %~dp0backend && python -u manage.py runserver --noreload"
timeout /t 2 /nobreak >nul

echo [2/3] Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d %~dp0frontend && npm run serve"
timeout /t 2 /nobreak >nul

echo [3/4] Starting Telegram Bot...
start "Telegram Bot" cmd /k "cd /d %~dp0bot && python bot.py"
timeout /t 2 /nobreak >nul

echo [4/4] Starting Auto Draw Scheduler...
start "Auto Draw Scheduler" cmd /k "cd /d %~dp0backend && python auto_draw_daemon.py"

echo.
echo ========================================
echo   All services started successfully!
echo ========================================
echo.
echo Four service windows have been opened.
echo Please do not close them.
echo.
echo Services:
echo   - Frontend: http://localhost:8080
echo   - Backend API: http://localhost:8000/api
echo   - Admin Panel: http://localhost:8000/admin (admin/admin123)
echo   - Telegram Bot: Running
echo   - Auto Draw Scheduler: Running (check every 60s)
echo.
echo Press any key to close this window...
pause >nul
