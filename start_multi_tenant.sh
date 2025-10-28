#!/bin/bash

# Telegram Lottery Bot System - Multi-Tenant Mode (Hot Reload)
# Linux/Mac 启动脚本

# 设置颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}  🎉 Telegram 抽奖系统 - 多租户模式 (热重载)${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}💡 本启动脚本将启动以下服务：${NC}"
echo "   1. Django 后端 API 服务器"
echo "   2. Vue 前端管理界面"
echo "   3. 多租户 Bot 程序 (支持热重载)"
echo "   4. 自动开奖守护进程"
echo ""
echo -e "${YELLOW}⚡ 特性：${NC}"
echo "   ✓ 支持多个租户同时使用"
echo "   ✓ 每个租户配置自己的 Bot Token"
echo "   ✓ 热重载：配置后自动启动 Bot"
echo "   ✓ 数据完全隔离"
echo ""
echo -e "${BLUE}============================================================${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 检查依赖
echo -e "${GREEN}[检查] 检查依赖...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 python3${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 npm${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 依赖检查通过${NC}"
echo ""

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"

# 启动后端
echo -e "${GREEN}[1/4] 🚀 启动后端服务器...${NC}"
cd "$SCRIPT_DIR/backend"
nohup python3 manage.py runserver 0.0.0.0:8000 --noreload > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
BACKEND_PID=$!
echo "   ✓ 后端启动 (PID: $BACKEND_PID)"
echo "$BACKEND_PID" > "$SCRIPT_DIR/logs/backend.pid"
sleep 2

# 启动前端
echo -e "${GREEN}[2/4] 🎨 启动前端管理界面...${NC}"
cd "$SCRIPT_DIR/frontend"
nohup npm run serve > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "   ✓ 前端启动 (PID: $FRONTEND_PID)"
echo "$FRONTEND_PID" > "$SCRIPT_DIR/logs/frontend.pid"
sleep 2

# 启动多租户Bot
echo -e "${GREEN}[3/4] 🤖 启动多租户Bot程序 (热重载模式)...${NC}"
cd "$SCRIPT_DIR/bot"
nohup python3 multi_tenant_bot.py > "$SCRIPT_DIR/logs/bot.log" 2>&1 &
BOT_PID=$!
echo "   ✓ Bot启动 (PID: $BOT_PID)"
echo "$BOT_PID" > "$SCRIPT_DIR/logs/bot.pid"
sleep 2

# 启动自动开奖守护进程
echo -e "${GREEN}[4/4] ⏰ 启动自动开奖守护进程...${NC}"
cd "$SCRIPT_DIR/backend"
nohup python3 auto_draw_daemon.py > "$SCRIPT_DIR/logs/auto_draw.log" 2>&1 &
AUTO_DRAW_PID=$!
echo "   ✓ 自动开奖启动 (PID: $AUTO_DRAW_PID)"
echo "$AUTO_DRAW_PID" > "$SCRIPT_DIR/logs/auto_draw.pid"
sleep 1

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}  ✅ 所有服务已成功启动！${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}📋 进程信息：${NC}"
echo "   • Backend API:      PID $BACKEND_PID"
echo "   • Frontend:         PID $FRONTEND_PID"
echo "   • Multi-Tenant Bot: PID $BOT_PID"
echo "   • Auto Draw:        PID $AUTO_DRAW_PID"
echo ""
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}🌐 访问地址：${NC}"
echo "   • 前端管理界面: http://localhost:8080"
echo "   • 后端 API:     http://localhost:8000/api"
echo "   • Django 管理:  http://localhost:8000/admin"
echo ""
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}📝 首次使用步骤：${NC}"
echo ""
echo "   1️⃣  访问 http://localhost:8080"
echo "   2️⃣  登录您的账号 (没有请先注册)"
echo "   3️⃣  点击导航栏的 'Bot配置'"
echo "   4️⃣  配置您的 Telegram Bot Token"
echo "   5️⃣  保存后 10秒内 Bot 会自动启动 ✨"
echo ""
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}🔥 热重载功能说明：${NC}"
echo ""
echo "   • Bot程序启动后会持续监控数据库配置"
echo "   • 即使启动时没有配置 Token，也会自动等待"
echo "   • 配置后 10秒内自动启动对应的 Bot"
echo "   • 修改配置 10秒内自动重启 Bot"
echo "   • 禁用配置 10秒内自动停止 Bot"
echo "   • 完全不需要手动重启 Bot 程序！"
echo ""
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}📖 日志文件：${NC}"
echo "   • Backend:  logs/backend.log"
echo "   • Frontend: logs/frontend.log"
echo "   • Bot:      logs/bot.log"
echo "   • AutoDraw: logs/auto_draw.log"
echo ""
echo -e "${YELLOW}🛑 停止服务：${NC}"
echo "   运行: ./stop_all.sh"
echo "   或手动: kill -9 $BACKEND_PID $FRONTEND_PID $BOT_PID $AUTO_DRAW_PID"
echo ""
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${GREEN}🎊 准备就绪！开始使用吧！${NC}"
echo ""

