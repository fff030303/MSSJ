import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/Register.vue')
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'question',
        name: 'QuestionSubmit',
        component: () => import('../views/question/QuestionSubmit.vue')
      },
      {
        path: 'answer/:id',
        name: 'AnswerDisplay',
        component: () => import('../views/answer/AnswerDisplay.vue'),
        props: true
      },
      {
        path: 'history',
        name: 'HistoryQuery',
        component: () => import('../views/history/HistoryQuery.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/settings/Settings.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 导航守卫，用于身份验证
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token')
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router 