import { BASE_URL } from '@/config.js'

const ADMIN_TOKEN_KEY = 'admin_token'

function getAdminToken() {
  return uni.getStorageSync(ADMIN_TOKEN_KEY) || ''
}

// 管理员登录
export function adminLogin(username, password) {
  return request('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `username=${username}&password=${password}&grant_type=password`
  })
}

// 辅助函数：使用 admin token 的请求
function adminRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const method = options.method || 'GET'
    const token = getAdminToken()

    const header = {
      'Content-Type': 'application/json',
      ...options.headers
    }

    if (token) {
      header.Authorization = `Bearer ${token}`
    }

    const data = method === 'GET' ? undefined : (options.body || {})

    uni.request({
      url: BASE_URL + url,
      method,
      header,
      data,
      success: (res) => {
        if (res.statusCode >= 400) {
          reject(res.data || '请求失败')
        } else {
          resolve(res.data)
        }
      },
      fail: (err) => {
        reject(err || '网络错误')
      }
    })
  })
}

// 获取认养对象列表
export function getAdminTargets() {
  return adminRequest('/admin/targets', { method: 'GET' })
}

// 创建认养对象
export function createAdminTarget(targetData) {
  return adminRequest('/admin/targets', {
    method: 'POST',
    body: targetData
  })
}

// 获取所有订单（管理员视角）
export function getAdminOrders() {
  return adminRequest('/admin/orders', { method: 'GET' })
}

// 手动创建订单
export function createAdminOrder(orderData) {
  return adminRequest('/admin/orders', {
    method: 'POST',
    body: orderData
  })
}

// 发布更新
export function createUpdate(updateData) {
  return adminRequest('/admin/updates', {
    method: 'POST',
    body: updateData
  })
}

// 创建配送记录
export function createDelivery(deliveryData) {
  return adminRequest('/admin/deliveries', {
    method: 'POST',
    body: deliveryData
  })
}
