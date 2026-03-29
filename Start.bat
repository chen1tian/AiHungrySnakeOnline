@echo off
chcp 65001 >nul
title 贪吃蛇Online 启动器

echo ========================================
echo   贪吃蛇Online - 同时启动前后台
echo ========================================
echo.

:: 启动后端 (FastAPI + Uvicorn)
echo [1/2] 启动后端服务...
start "Backend - 贪吃蛇Online" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: 启动前端 (Vite Dev Server)
echo [2/2] 启动前端服务...
start "Frontend - 贪吃蛇Online" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo 前后台已启动！
echo   后端: http://localhost:8000
echo   前端: http://localhost:5173
echo.
echo 关闭此窗口不会影响已启动的服务。
echo 如需停止，请关闭对应的命令行窗口。
pause
