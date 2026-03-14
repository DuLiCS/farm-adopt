#!/usr/bin/env python3
"""
节气自动日志生成脚本
每天由cron触发，检查今天是否是节气，是则调模型生成草稿
"""

import requests
import os
from datetime import datetime
import sxtwl

SERVER_URL = "http://47.102.138.74"
ADMIN_USER = "admin"
ADMIN_PASS = "farm2026"
DEVICE_ID = "esp32-farm-01"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = "stepfun/step-3.5-flash:free"

SOLAR_TERM_NAMES = [
    "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
    "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
    "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
    "寒露", "霜降", "立冬", "小雪", "大雪", "冬至"
]

SOLAR_TERM_DESC = {
    "小寒": "天寒地冻，万物蛰伏",
    "大寒": "一年中最寒冷的时节",
    "立春": "春回大地，万象更新",
    "雨水": "降水开始增多，气温回升",
    "惊蛰": "春雷乍动，万物复苏",
    "春分": "昼夜平分，春意正浓",
    "清明": "天清地明，茶树萌芽",
    "谷雨": "雨水增多，春茶丰收",
    "立夏": "夏季开始，万物生长",
    "小满": "麦类作物籽粒渐满",
    "芒种": "有芒的麦子快收，稻子可种",
    "夏至": "白昼最长，暑热正盛",
    "小暑": "天气开始炎热",
    "大暑": "一年中最热的时节",
    "立秋": "秋季开始，暑气渐消",
    "处暑": "暑气至此而止",
    "白露": "天气转凉，露水凝结",
    "秋分": "昼夜平分，秋意渐深",
    "寒露": "气温更低，露水更寒",
    "霜降": "天气渐冷，开始有霜",
    "立冬": "冬季开始，万物收藏",
    "小雪": "开始降雪，但雪量不大",
    "大雪": "降雪量增多",
    "冬至": "白昼最短，阴极阳生"
}

def get_today_solar_term():
    today = datetime.now()
    day = sxtwl.fromSolar(today.year, today.month, today.day)
    if day.hasJieQi():
        jq_index = day.getJieQi()
        name = SOLAR_TERM_NAMES[jq_index]
        desc = SOLAR_TERM_DESC.get(name, "")
        return name, desc
    return None, None

def get_latest_sensor():
    try:
        res = requests.get(
            f"{SERVER_URL}/api/sensor/latest?device_id={DEVICE_ID}",
            timeout=5
        )
        return res.json()
    except:
        return None

def get_admin_token():
    try:
        res = requests.post(
            f"{SERVER_URL}/auth/login",
            data={"username": ADMIN_USER, "password": ADMIN_PASS},
            timeout=5
        )
        return res.json().get("access_token")
    except Exception as e:
        print(f"获取token失败: {e}")
        return None

def generate_log(solar_term_name, solar_term_desc, sensor):
    sensor_text = ""
    if sensor and sensor.get("temperature"):
        sensor_text = f"今日农庄实测：温度{sensor['temperature']}°C，湿度{sensor['humidity']}%。"

    prompt = f"""你是山南记农庄的文字记录者。今天是{solar_term_name}节气，{solar_term_desc}。{sensor_text}

请以农庄主人的口吻，写一篇简短的节气农庄日志（150字左右）。
要求：
- 结合节气特点和茶树/植物的生长状态
- 语言朴实有温度，带有生活哲学气息
- 不要说"山南记"这个词，用"这里"或"农庄"代替
- 结尾可以有一句对认养主人的话

只输出正文，不要标题，不要多余说明。"""

    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=30
    )
    data = res.json()
    return data["choices"][0]["message"]["content"]

def post_draft(token, solar_term_name, content):
    res = requests.post(
        f"{SERVER_URL}/admin/updates",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "target_id": 1,
            "title": f"{solar_term_name} · 农庄手记",
            "description": content,
            "log_type": "solar_term",
            "status": "draft",
            "source": "auto"
        },
        timeout=10
    )
    return res.status_code == 201

def main():
    solar_term_name, solar_term_desc = get_today_solar_term()
    if not solar_term_name:
        print("今天不是节气，跳过")
        return

    print(f"今天是{solar_term_name}，开始生成日志...")
    sensor = get_latest_sensor()
    print(f"传感器数据：{sensor}")

    content = generate_log(solar_term_name, solar_term_desc, sensor)
    print(f"生成内容：{content[:80]}...")

    token = get_admin_token()
    if not token:
        print("获取管理员token失败")
        return

    ok = post_draft(token, solar_term_name, content)
    print("草稿发布成功" if ok else "草稿发布失败")

if __name__ == "__main__":
    main()
