/**
 * 文件名：router/index.js
 * 描述：应用路由配置文件
 * 作者：Li zekun
 * 创建日期：2026-04-08
 * 最后修改：2026-04-08
 */

import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../store'
import { authApi } from '../api'
import { normalizeAccessToken } from '../utils/accessToken'

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
    component: () => import('../views/SystemLayout.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true
    },
    children: [
      {
        path: '',
        redirect: '/admin/organization'
      },
      {
        path: '/admin/organization',
        name: 'Organization',
        meta: { requiresAuth: true, requiresAdmin: true },
        component: () => import('../views/admin/Organization.vue')
      },
      {
        path: '/admin/user-approval',
        name: 'UserApproval',
        meta: { requiresAuth: true, requiresAdmin: true },
        component: () => import('../views/admin/UserApproval.vue')
      },
      {
        path: '/admin/user-management',
        name: 'UserManagement',
        meta: { requiresAuth: true, requiresAdmin: true },
        component: () => import('../views/admin/UserManagement.vue')
      },
      {
        path: '/admin/role',
        name: 'Role',
        meta: { requiresAuth: true, requiresAdmin: true },
        component: () => import('../views/admin/Role.vue')
      },
      {
        path: '/admin/authorization',
        name: 'Authorization',
        meta: { requiresAuth: true, requiresAdmin: true },
        component: () => import('../views/admin/Authorization.vue')
      },
      {
        path: '/admin/data',
        name: 'Data',
        meta: { requiresAuth: true, requiresAdmin: true },
        component: () => import('../views/admin/DataLayout.vue'),
        redirect: '/admin/data/online-users',
        children: [
          {
            path: 'online-users',
            name: 'DataOnlineUsers',
            meta: { requiresAuth: true, requiresAdmin: true },
            component: () => import('../views/admin/DataOnlineUsers.vue')
          },
          {
            path: 'logs',
            name: 'DataLogs',
            meta: { requiresAuth: true, requiresAdmin: true },
            component: () => import('../views/admin/DataLogs.vue')
          },
          {
            path: 'backup',
            name: 'DataBackup',
            meta: { requiresAuth: true, requiresAdmin: true },
            component: () => import('../views/admin/DataBackupPage.vue')
          },
          {
            path: 'restore',
            name: 'DataRestore',
            meta: { requiresAuth: true, requiresAdmin: true },
            component: () => import('../views/admin/DataRestorePage.vue')
          }
        ]
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：校验 Token 与用户信息；系统管理类路由仅管理员可进
//注意：Vue Router 4 子路由默认不继承父级 meta，必须用 matched 聚合判断是否需要登录
router.beforeEach(async (to, from, next) => {
  const token = normalizeAccessToken(localStorage.getItem('token'))
  const requiresAuth = to.matched.some((r) => r.meta.requiresAuth)

  if (requiresAuth) {
    if (!token) {
      next({ name: 'Login' })
      return
    }

    // Token 与 profile_synced_token 不一致时需拉取 profile；登录页已先 getProfile 并写入 synced，此处不再重复请求
    const synced = typeof sessionStorage !== 'undefined'
      ? sessionStorage.getItem('profile_synced_token')
      : null
    const needProfileSync = !synced || token !== synced

    if (needProfileSync) {
      try {
        const res = await authApi.getProfile(token)
        if (res.code === 200 && res.data) {
          const userStore = useUserStore()
          userStore.login(token, res.data)
          if (typeof sessionStorage !== 'undefined') {
            sessionStorage.setItem('profile_synced_token', token)
          }
        } else {
          const userStore = useUserStore()
          userStore.logout()
          next({ name: 'Login' })
          return
        }
      } catch (e) {
        const userStore = useUserStore()
        userStore.logout()
        next({ name: 'Login' })
        return
      }
    }

    const needsAdmin = to.matched.some((r) => r.meta.requiresAdmin)
    if (needsAdmin) {
      const userStore = useUserStore()
      if (userStore.userInfo?.role !== 'admin') {
        ElMessage.warning('需要管理员权限')
        next({ path: '/home' })
        return
      }
    }

    next()
    return
  }

  const isAuthLayoutRoute = to.matched.some((r) => r.meta.layout === 'auth')
  if (isAuthLayoutRoute && token) {
    next({ name: 'Home' })
    return
  }

  next()
})

export default router
