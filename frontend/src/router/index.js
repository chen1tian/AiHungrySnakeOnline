import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/',
    name: 'Lobby',
    component: () => import('../views/Lobby.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/room/:roomId',
    name: 'Room',
    component: () => import('../views/Room.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/game/:roomId',
    name: 'Game',
    component: () => import('../views/Game.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && auth.isLoggedIn) {
    next({ name: 'Lobby' })
  } else {
    next()
  }
})

export default router
