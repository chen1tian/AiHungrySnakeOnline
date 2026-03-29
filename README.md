# 🐍 贪吃蛇Online - 多人在线PVP贪吃蛇

一个基于 FastAPI + Vue3 的多人在线贪吃蛇游戏。

## 功能特性

- 注册/登录账号系统
- 创建/加入游戏房间
- 自定义 emoji 蛇头和颜色
- 同色玩家自动组队
- PVP 对战：吃掉其他玩家增长
- 特殊苹果道具：加速、增长、无敌、时间减慢
- 死亡 5 秒后自动复活

## 技术栈

- **后端**: Python FastAPI + WebSocket + SQLAlchemy (SQLite)
- **前端**: Vue 3 + Vite + Pinia + HTML5 Canvas

## 启动方式

### Docker 部署（推荐）

```bash
docker compose up -d --build
```

浏览器打开 http://localhost 即可游玩。

停止服务：

```bash
docker compose down
```

### 本地开发

#### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

然后浏览器打开 http://localhost:3000 即可游玩。

## 操作说明

- **WASD** 或 **方向键** 控制蛇移动
- 撞到其他玩家（非同队）可以吃掉对方
- 撞到墙壁或自身会死亡，5 秒后复活
- 吃苹果可增长或获得特殊效果

## 特殊苹果

| 图标 | 效果 |
|------|------|
| 🍎 | 普通苹果，增长 1 格 |
| ⚡ | 加速，移动速度翻倍 5 秒 |
| 🌟 | 增长，一次增长 3 格 |
| 🛡️ | 无敌，随机 3/5/10 秒不可被击杀 |
| ⏳ | 时间减慢，所有人速度减半 5 秒 |
