const BASE = ''

function getToken() {
  return localStorage.getItem('admin_token')
}

export async function request(url, options = {}) {
  const isFormData = options.body instanceof FormData
  const res = await fetch(BASE + url, {
    ...options,
    headers: {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
      ...options.headers
    }
  })

  if (res.status === 401) {
    localStorage.removeItem('admin_token')
    location.href = '/login'
    return
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: '请求失败' }))
    throw err
  }

  return res.json()
}

export const api = {
  login: (username, password) =>
    fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `username=${username}&password=${password}`
    }).then(r => r.json()),

  getTargets: () => request('/admin/targets'),
  createTarget: (data) => request('/admin/targets', { method: 'POST', body: JSON.stringify(data) }),

  getOrders: () => request('/admin/orders'),
  createOrder: (data) => request('/admin/orders', { method: 'POST', body: JSON.stringify(data) }),

  getUsers: () => request('/admin/users'),

  getUpdates: () => request('/admin/updates'),
  createUpdate: (data) => request('/admin/updates', { method: 'POST', body: JSON.stringify(data) }),

  createDelivery: (data) => request('/admin/deliveries', { method: 'POST', body: JSON.stringify(data) }),

  uploadImage: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return request('/admin/upload', {
      method: 'POST',
      body: formData,
      headers: {
        // 不设置 Content-Type，让浏览器自动设置 boundary
      }
    })
  },

  updateTargetCover: (targetId, coverUrl) =>
    request(`/admin/targets/${targetId}/cover`, {
      method: 'PATCH',
      body: JSON.stringify({ cover_image: coverUrl })
    })
}