#!/usr/bin/env bash
set -e

BASE_URL="http://localhost:8000"
TEST_PHONE="13800138000"
TEST_PASSWORD="secret123"
TEST_NICKNAME="测试用户"

echo "=== Farm Adopt API 测试开始 ==="

# 1. 健康检查
echo -e "\n[1] 健康检查"
curl -s $BASE_URL/ | jq .

# 2. 注册
echo -e "\n[2] 注册用户"
REG_RESP=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"$TEST_PHONE\",\"password\":\"$TEST_PASSWORD\",\"nickname\":\"$TEST_NICKNAME\"}")
echo $REG_RESP | jq .

# 3. 登录
echo -e "\n[3] 登录获取 Token"
LOGIN_RESP=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$TEST_PHONE&password=$TEST_PASSWORD")
echo $LOGIN_RESP | jq .
ACCESS_TOKEN=$(echo $LOGIN_RESP | jq -r .access_token)

# 4. 初始化数据库（插入目标与订单）
echo -e "\n[4] 初始化测试数据（通过 psql）"
docker-compose exec -T postgres psql -U farm_user -d farm_adopt <<EOF
-- 插入认养目标（如果不存在）
INSERT INTO adopt_targets (type, code, location_desc, camera_id, current_status)
VALUES ('tea', 'TEA-001', '西湖龙井茶园', 'CAM-001', 'active')
ON CONFLICT (code) DO NOTHING;

-- 获取目标 ID
SELECT id FROM adopt_targets WHERE code='TEA-001' \gset

-- 插入用户（确保存在）
INSERT INTO users (phone, password_hash, nickname)
VALUES ('$TEST_PHONE', '$(python3 -c "from app.core.security import get_password_hash; print(get_password_hash('$TEST_PASSWORD'))" 2>/dev/null || echo 'dummy')', '$TEST_NICKNAME')
ON CONFLICT (phone) DO NOTHING;

-- 获取用户 ID
SELECT id FROM users WHERE phone='$TEST_PHONE' \gset

-- 插入订单（如果不存在）
INSERT INTO adopt_orders (user_id, target_id, plan_type, price, expire_date, status)
VALUES (:user_id, :target_id, 'annual', 1888.00, '2026-03-09', 'active')
ON CONFLICT DO NOTHING;
EOF

# 5. 查询我的订单
echo -e "\n[5] 查询我的订单"
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$BASE_URL/orders/me" | jq .

# 6. 查询更新记录
echo -e "\n[6] 查询更新记录"
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$BASE_URL/orders/1/updates" | jq .

# 7. 查询配送记录
echo -e "\n[7] 查询配送记录"
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$BASE_URL/orders/1/deliveries" | jq .

echo -e "\n=== 测试结束 ==="