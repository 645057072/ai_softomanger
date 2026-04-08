/**
 * 文件名：router/index.js
 * 描述：应用路由配置文件
 * 作者：Li zekun
 * 创建日期：2026-04-08
 * 最后修改：2026-04-08
 */

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
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
    path: '/admin/organization',
    name: 'Organization',
    component: () => import('../views/admin/Organization.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/admin/user-approval',
    name: 'UserApproval',
    component: () => import('../views/admin/UserApproval.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/admin/user-management',
    name: 'UserManagement',
    component: () => import('../views/admin/UserManagement.vue'),
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
