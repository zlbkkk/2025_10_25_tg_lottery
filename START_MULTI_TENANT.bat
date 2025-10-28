@echo off
chcp 65001 >nul
title Telegram Lottery Bot System - Multi-Tenant Mode (Hot Reload)
cls

echo ============================================================
echo   🎉 Telegram 抽奖系统 - 多租户模式 (热重载)
echo ============================================================
echo.
echo 💡 本启动脚本将启动以下服务：
echo    1. Django 后端 API 服务器
echo    2. Vue 前端管理界面
echo    3. 多租户 Bot 程序 (支持热重载)
echo    4. 自动开奖守护进程
echo.
echo ⚡ 特性：
echo    ✓ 支持多个租户同时使用
echo    ✓ 每个租户配置自己的 Bot Token
echo    ✓ 热重载：配置后自动启动 Bot
echo    ✓ 数据完全隔离
echo.
echo ============================================================
echo.

echo [1/4] 🚀 启动后端服务器...
start "Backend API Server" cmd /k "cd /d %~dp0backend && echo 后端服务器启动中... && python -u manage.py runserver 0.0.0.0:8000 --noreload"
timeout /t 3 /nobreak >nul

echo [2/4] 🎨 启动前端管理界面...
start "Frontend Admin Panel" cmd /k "cd /d %~dp0frontend && echo 前端界面启动中... && npm run serve"
timeout /t 3 /nobreak >nul

echo [3/4] 🤖 启动多租户Bot程序 (热重载模式)...
start "Multi-Tenant Bot (Hot Reload)" cmd /k "cd /d %~dp0bot && echo 多租户Bot启动中 (热重载模式)... && echo. && echo 💡 提示：Bot会自动监控配置变化 && echo    - 新增配置 → 自动启动Bot && echo    - 修改Token → 自动重启Bot && echo    - 禁用配置 → 自动停止Bot && echo. && python multi_tenant_bot.py"
timeout /t 3 /nobreak >nul

echo [4/4] ⏰ 启动自动开奖守护进程...
start "Auto Draw Scheduler" cmd /k "cd /d %~dp0backend && echo 自动开奖守护进程启动中... && python auto_draw_daemon.py"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo   ✅ 所有服务已成功启动！
echo ============================================================
echo.
echo 📋 已打开 4 个服务窗口，请不要关闭它们：
echo.
echo   [窗口1] Backend API Server
echo   [窗口2] Frontend Admin Panel  
echo   [窗口3] Multi-Tenant Bot (热重载)
echo   [窗口4] Auto Draw Scheduler
echo.
echo ============================================================
echo.
echo 🌐 访问地址：
echo   • 前端管理界面: http://localhost:8080
echo   • 后端 API:     http://localhost:8000/api
echo   • Django 管理:  http://localhost:8000/admin
echo.
echo ============================================================
echo.
echo 📝 首次使用步骤：
echo.
echo   1️⃣  访问 http://localhost:8080
echo   2️⃣  登录您的账号 (没有请先注册)
echo   3️⃣  点击导航栏的 "Bot配置"
echo   4️⃣  配置您的 Telegram Bot Token
echo   5️⃣  保存后 10秒内 Bot 会自动启动 ✨
echo.
echo ============================================================
echo.
echo 🔥 热重载功能说明：
echo.
echo   • Bot程序启动后会持续监控数据库配置
echo   • 即使启动时没有配置 Token，也会自动等待
echo   • 配置后 10秒内自动启动对应的 Bot
echo   • 修改配置 10秒内自动重启 Bot
echo   • 禁用配置 10秒内自动停止 Bot
echo   • 完全不需要手动重启 Bot 程序！
echo.
echo ============================================================
echo.
echo ⚠️  注意事项：
echo.
echo   • 首次启动前端可能需要等待 1-2 分钟 (npm 编译)
echo   • 确保端口 8080 和 8000 未被占用
echo   • 如需停止服务，直接关闭对应窗口即可
echo   • 停止所有服务：关闭所有打开的窗口
echo.
echo ============================================================
echo.
echo 📖 详细文档：
echo   • 多租户Bot启动指南.md
echo   • Bot热重载功能说明.md
echo   • 用户管理指南.md
echo.
echo ============================================================
echo.
echo 🎊 准备就绪！开始使用吧！
echo.
echo 按任意键关闭此窗口...
echo (关闭此窗口不会影响服务运行)
echo.
pause >nul

