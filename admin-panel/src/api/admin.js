import { BASE_URL } from '@/config.js'

const ADMIN_TOKEN_KEY = 'admin_token'

function getAdminToken() {
  return localStorage.getItem(ADMIN_TOKEN_KEY) || ''
}

function setAdminToken(token) {
  localStorage.setItem(ADMIN_TOKEN_KEY, token)
}

function adminRequest(url, options = {}) {
  const method = options.method || 'GET'
  const token = getAdminToken()

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const fetchOptions = {
    method,
    headers,
    credentials: 'include'
  }

  if (method !== 'GET' && options.body) {
    fetchOptions.body = JSON.stringify(options.body)
  }

  return fetch(BASE_URL + url, fetchOptions)
    .then(async (res) => {
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || data.message || '请求失败')
      }
      return data
    })
}

// 管理员登录（使用 form-urlencoded）
export function adminLogin(username, password) {
  const body = new URLSearchParams({
    username,
    password,
    grant_type: 'password'
  })
  // 使用相对路径，通过 Vite 代理
  return fetch(BASE_URL + '/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: body,
    redirect: 'manual'
  }).then(async (res) => {
    const data = await res.json()
    console.log('Login response:', res.status, data)
    if (!res.ok) {
      throw new Error(data.detail || data.message || '登录失败')
    }
    setAdminToken(data.access_token)
    return data
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

// 获取所有更新记录
export function getAdminUpdates() {
  return adminRequest('/admin/updates', { method: 'GET' })
}

// 获取所有用户列表（管理员）
export function getAdminUsers() {
  return adminRequest('/admin/users', { method: 'GET' })
}
