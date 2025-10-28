# 多租户多机器人启动指南（Polling模式）

## 🎯 概述

本系统支持多个租户（老板）同时使用，每个租户配置自己的 Telegram Bot Token，系统会为每个租户启动独立的 Bot 进程，实现完全的数据隔离。

## 📋 架构说明

```
┌─────────────────────────────────────────────────────┐
│          多租户抽奖Bot系统 (Polling模式)              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  租户A (admin用户)                                  │
│  ├─ Bot Token: 123456:ABC...                       │
│  ├─ Bot进程: Process-A                             │
│  └─ 数据: Lottery (admin_user_id=A)                │
│                                                     │
│  租户B (user2)                                      │
│  ├─ Bot Token: 789012:DEF...                       │
│  ├─ Bot进程: Process-B                             │
│  └─ 数据: Lottery (admin_user_id=B)                │
│                                                     │
│  租户C (user3)                                      │
│  ├─ Bot Token: 345678:GHI...                       │
│  ├─ Bot进程: Process-C                             │
│  └─ 数据: Lottery (admin_user_id=C)                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 🚀 使用步骤

### 方式A：先启动Bot，后配置Token（推荐 ⭐ 支持热重载）

#### 1. 启动多租户Bot系统

```powershell
# Windows
cd tg_choujiang/bot
python multi_tenant_bot.py
```

```bash
# Linux/Mac
cd tg_choujiang/bot
python3 multi_tenant_bot.py
```

**Bot会持续运行，等待配置：**
```
============================================================
🚀 多租户抽奖Bot系统启动中（热重载模式）...
============================================================
💡 提示：系统会自动监控配置变化
   - 新增配置 → 自动启动Bot
   - 修改Token → 自动重启Bot
   - 禁用配置 → 自动停止Bot
============================================================
⚠️  暂无激活的Bot配置
📝 请通过后台管理页面配置Bot Token
🔄 将在 10 秒后重新检查...
```

#### 2. 配置Bot Token（后台管理页面）

1. 登录管理后台（使用您的账号）
2. 点击导航栏的 **"Bot配置"**
3. 创建您的 Telegram Bot：
   - 在 Telegram 搜索 `@BotFather`
   - 发送 `/newbot` 命令
   - 按提示设置 Bot 名称和用户名
   - 复制 BotFather 返回的 Token
4. 在后台粘贴 Token 并保存
5. 点击 **"测试连接"** 验证配置

#### 3. 观察Bot自动启动

**10秒内，Bot程序会自动检测到新配置并启动：**
```
🆕 发现新配置，启动Bot: admin (User ID: 1)
✅ [admin] Bot启动成功！
📊 当前运行: 1 个Bot | 下次检查: 10秒后
```

**完全自动，无需手动重启！** 🎉

---

### 方式B：先配置Token，后启动Bot（传统方式）

#### 1. 配置Bot Token（后台管理页面）

1. 登录管理后台
2. 配置Bot Token
3. 保存

#### 2. 启动多租户Bot系统

#### Windows (PowerShell)

```powershell
cd tg_choujiang/bot
python multi_tenant_bot.py
```

#### Linux/Mac

```bash
cd tg_choujiang/bot
python3 multi_tenant_bot.py
```

### 3. 查看启动日志

系统启动后会显示类似以下日志：

```
============================================================
🚀 多租户抽奖Bot系统启动中...
============================================================
📊 找到 3 个激活的租户Bot
🔧 启动租户Bot: admin (User ID: 1)
🔧 启动租户Bot: boss2 (User ID: 2)
🔧 启动租户Bot: boss3 (User ID: 3)
============================================================
✅ 所有Bot进程已启动！共 3 个
============================================================
2024-01-01 10:00:00 - [12345] ✅ [admin] Bot启动成功！
2024-01-01 10:00:01 - [12346] ✅ [boss2] Bot启动成功！
2024-01-01 10:00:02 - [12347] ✅ [boss3] Bot启动成功！
```

### 4. 运行中管理Bot

#### 添加新租户
1. 新用户注册账号
2. 登录后配置Bot Token
3. 保存 → **10秒内自动启动新Bot** ✨

#### 修改Token
1. 登录后台
2. 修改Bot配置
3. 保存 → **10秒内自动重启对应Bot** ✨

#### 禁用Bot
1. 登录后台
2. 关闭"启用状态"开关
3. 保存 → **10秒内自动停止Bot** ✨

**所有操作都是自动的，无需手动重启！**

### 5. 停止Bot系统

按 `Ctrl + C` 停止所有Bot进程。

## 🔐 数据隔离说明

### 自动隔离

- 每个租户只能看到和管理自己创建的抽奖活动
- Bot 自动根据租户ID过滤数据
- 用户参与抽奖时，只能看到对应租户的活动

### 数据过滤机制

```python
# 后端自动过滤
lotteries = Lottery.objects.filter(admin_user_id=request.user.id)

# Bot自动隔离
service = DjangoService(admin_user_id)  # 每个Bot一个实例
```

## 📝 核心文件说明

### 后端

- `backend/lottery/models.py` - 添加了 `BotConfig` 模型
- `backend/lottery/auth_views.py` - 添加了 `bot_config_view` API
- `backend/lottery/serializers.py` - 添加了 `BotConfigSerializer`

### Bot

- `bot/multi_tenant_bot.py` - **多租户启动脚本**（新）
- `bot/services/django_service.py` - Django数据服务（支持租户隔离）
- `bot/handlers/*.py` - 处理器已支持 `admin_user_id` 参数

### 前端

- `frontend/src/views/BotConfig.vue` - Bot配置页面
- `frontend/src/api/index.js` - 添加了 Bot配置API

## ⚠️ 重要提示

### 1. 进程管理

- 每个租户一个独立进程
- 修改 Bot Token 后需要**重启**系统
- 建议使用 `supervisor` 或 `systemd` 管理进程（生产环境）

### 2. 性能建议

- Polling 模式适合租户数 < 20
- 如果租户数超过 20，建议升级到 Webhook 模式
- 每个 Bot 会持续轮询 Telegram 服务器

### 3. Token 安全

- Bot Token 以加密形式存储在数据库
- API 返回时只显示前 10 个字符 + `***`
- 不要在日志中输出完整 Token

## 🔧 故障排查

### Bot 无法自动启动

**症状：** 配置保存后，10秒内Bot没有启动

**排查：**
1. 检查Bot程序是否正在运行
2. 查看终端是否有错误日志
3. 确认"启用状态"开关是否打开
4. 验证Token格式是否正确（`数字:字母数字`）
5. 检查数据库连接

### Bot 无法自动重启

**症状：** 修改Token后，Bot没有重启

**排查：**
1. 等待至少10秒（检查间隔）
2. 检查是否真的修改了Token（不只是空格）
3. 查看终端日志是否有"配置已更新"提示
4. 确认数据库记录是否已更新

### Bot 频繁重启

**症状：** Bot每10秒重启一次

**原因：** Token可能无效或网络问题

**解决：**
1. 使用"测试连接"功能验证Token
2. 检查网络是否能访问Telegram API
3. 向BotFather确认Token是否有效

### 配置修改不生效

**症状：** 修改配置后，Bot行为没变化

**排查：**
1. 确认已点击"保存配置"
2. 等待10秒让热重载生效
3. 查看终端是否有重启日志
4. 刷新数据库确认修改已保存

### 数据未隔离

**症状：** 看到其他租户的数据

**排查：**
1. 确认 `admin_user_id` 字段已设置
2. 检查后端 API 是否正确过滤
3. 运行数据库迁移：`python manage.py migrate`
4. 重启后端服务

## 📈 升级到 Webhook 模式

如果需要支持更多租户或降低服务器负载，可以升级到 Webhook 模式：

### 优势

- ✅ 支持无限租户
- ✅ 服务器资源占用低
- ✅ 消息推送更及时

### 要求

- 🔹 需要域名和SSL证书
- 🔹 需要公网IP
- 🔹 需要配置 Nginx

详见：`多租户多机器人实施方案.md`

## 📞 技术支持

如有问题，请检查：

1. 后端日志：`backend/logs/`
2. Bot日志：终端输出
3. 数据库：`bot_configs` 表

---

**祝使用愉快！🎉**

