import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/fortune' },
  { path: '/auth', name: 'Auth', component: () => import('../views/AuthPage.vue') },
  { path: '/fortune', name: 'Fortune', component: () => import('../views/FortunePage.vue') },
  { path: '/cards', name: 'Cards', component: () => import('../views/CardRevealPage.vue') },
  { path: '/payment/:readingId', name: 'Payment', component: () => import('../views/PaymentPage.vue') },
  { path: '/detail/:readingId', name: 'Detail', component: () => import('../views/DetailedReadingPage.vue') },
  { path: '/share/:readingId', name: 'Share', component: () => import('../views/SharePage.vue') },
  { path: '/profile', name: 'Profile', component: () => import('../views/ProfilePage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (!token && to.path !== '/auth') {
    return '/auth'
  }
  if (token && to.path === '/auth') {
    return '/fortune'
  }
})

export default router
