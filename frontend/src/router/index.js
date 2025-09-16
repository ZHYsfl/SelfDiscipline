import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Pair from '../views/Pair.vue'
import Habits from '../views/Habits.vue'
import { getAccessToken } from '../services/auth'

const routes = [
  { path: '/login', name: 'login', component: Login },
  { path: '/', name: 'dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/pair', name: 'pair', component: Pair, meta: { requiresAuth: true } },
  { path: '/habits', name: 'habits', component: Habits, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  if (to.meta.requiresAuth && !getAccessToken()) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }
  next()
})

export default router
