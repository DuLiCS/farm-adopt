"""
迁移脚本：给 adopt_orders 表添加 dedication 字段
用 IF NOT EXISTS，可以安全重复执行

使用方法（在服务器上，项目根目录）：
    python scripts/migrate_add_dedication.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine

SQL = """
ALTER TABLE adopt_orders
ADD COLUMN IF NOT EXISTS dedication VARCHAR(100);
"""

def run():
    with engine.connect() as conn:
        conn.execute(text(SQL))
        conn.commit()
        print("✅ 迁移完成：adopt_orders.dedication 字段已添加")

        # 验证
        result = conn.execute(text(
            "SELECT column_name, data_type, character_maximum_length "
            "FROM information_schema.columns "
            "WHERE table_name='adopt_orders' AND column_name='dedication'"
        ))
        row = result.fetchone()
        if row:
            print(f"   字段确认：{row[0]} {row[1]}({row[2]})")
        else:
            print("⚠️  字段未找到，请检查数据库连接")

if __name__ == "__main__":
    run()
