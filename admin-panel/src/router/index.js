import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import AdminLayout from '../views/AdminLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import Targets from '../views/Targets.vue'
import Orders from '../views/Orders.vue'
import UpdateForm from '../views/UpdateForm.vue'
import UpdateList from '../views/UpdateList.vue'
import Sensor from '../views/Sensor.vue'

const router = createRouter({
  history: createWebHistory('/admin-panel/'),
  routes: [
    { path: '/login', component: Login },
    {
      path: '/',
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', component: Dashboard },
        { path: 'targets', component: Targets },
        { path: 'orders', component: Orders },
        { path: 'updates', component: UpdateForm },
        { path: 'update-list', component: UpdateList },
        { path: 'sensor', component: Sensor }
      ]
    }
  ]
})

router.beforeEach(to => {
  if (to.meta.requiresAuth && !localStorage.getItem('admin_token')) {
    return '/login'
  }
})

export default router
