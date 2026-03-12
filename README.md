# Farm Adopt API

农庄认养系统后端骨架 (FastAPI + PostgreSQL + Alembic)

## 快速启动

1. 复制环境变量文件
   ```bash
   cp .env.example .env
   ```
   根据需要修改 `.env` 中的配置（特别是 `SECRET_KEY` 和 `POSTGRES_PASSWORD`）。

2. 启动服务
   ```bash
   docker-compose up --build
   ```

3. 访问
   - API 文档: http://localhost:8000/docs
   - 健康检查: http://localhost:8000/

## 数据库迁移

Alembic 已集成，容器启动时会自动运行 `alembic upgrade head`。

如需手动运行（在 app 容器内）：
```bash
alembic upgrade head
```

## 接口列表

- `POST /auth/register` 注册
- `POST /auth/login` 登录
- `GET /orders/me` 查询我的订单
- `GET /orders/{order_id}/updates` 查询认养对象更新
- `GET /orders/{order_id}/deliveries` 查询履约记录

## 项目结构

```
farm-adopt/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── adopt_target.py
│   │   ├── adopt_order.py
│   │   ├── update_log.py
│   │   └── delivery_log.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── adopt_target.py
│   │   ├── adopt_order.py
│   │   ├── update_log.py
│   │   └── delivery_log.py
│   ├── routers/
│   │   ├── auth.py
│   │   └── orders.py
│   └── core/
│       ├── config.py
│       └── security.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## 注意事项

- 数据库首次启动会自动创建表结构（通过 Alembic）。
- JWT 密钥请务必在生产环境更改。
- 当前未实现支付、管理后台、前端等。