import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/styles/index.css'

const app = createApp(App)
const pinia = createPinia()

// Pinia 必须在 Router 之前注册，否则路由守卫内 useUserStore() 可能未就绪
app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')
