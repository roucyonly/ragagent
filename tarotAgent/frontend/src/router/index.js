import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Login', component: () => import('../views/LoginPage.vue') },
  { path: '/topic', name: 'Topic', component: () => import('../views/TopicSelectPage.vue') },
  { path: '/cards', name: 'Cards', component: () => import('../views/CardSelectPage.vue') },
  { path: '/brief/:readingId', name: 'Brief', component: () => import('../views/BriefReadingPage.vue') },
  { path: '/payment/:readingId', name: 'Payment', component: () => import('../views/PaymentPage.vue') },
  { path: '/detail/:readingId', name: 'Detail', component: () => import('../views/DetailedReadingPage.vue') },
  { path: '/share/:readingId', name: 'Share', component: () => import('../views/SharePage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
