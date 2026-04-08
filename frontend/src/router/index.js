import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
    meta: {
      layout: 'auth'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/Register.vue'),
    meta: {
      layout: 'auth'
    }
  },
  {
    path: '/bi',
    name: 'BI',
    component: () => import('../views/BI.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/study',
    name: 'Study',
    component: () => import('../views/Study.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/paper',
    name: 'Paper',
    component: () => import('../views/Paper.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/exam',
    name: 'Exam',
    component: () => import('../views/Exam.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/system',
    name: 'System',
    component: () => import('../views/System.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/questions',
    name: 'Questions',
    component: () => import('../views/Questions.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/papers',
    name: 'Papers',
    component: () => import('../views/Papers.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/exams',
    name: 'Exams',
    component: () => import('../views/Exams.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/scores',
    name: 'Scores',
    component: () => import('../views/Scores.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/exam/:id',
    name: 'TakeExam',
    component: () => import('../views/TakeExam.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/review/:id',
    name: 'ReviewExam',
    component: () => import('../views/ReviewExam.vue'),
    meta: {
      requiresAuth: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth) {
    if (token) {
      next()
    } else {
      next({ name: 'Login' })
    }
  } else if (to.meta.layout === 'auth' && token) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
