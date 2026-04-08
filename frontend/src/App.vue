<!--
  文件名：App.vue
  描述：应用主组件，处理布局切换
  作者：Li zekun
  创建日期：2026-04-08
  最后修改：2026-04-08
-->

<template>
  <div id="app">
    <template v-if="isAuthLayout">
      <router-view />
    </template>
    <template v-else-if="isLoggedIn">
      <Layout>
        <router-view />
      </Layout>
    </template>
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script>
import Layout from './components/Layout.vue'
import { useUserStore } from './store'

export default {
  name: 'App',
  components: {
    Layout
  },
  computed: {
    isLoggedIn() {
      const userStore = useUserStore()
      return userStore.isLoggedIn
    },
    isAuthLayout() {
      const currentRoute = this.$route
      return currentRoute.meta.layout === 'auth'
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

#app {
  width: 100%;
  height: 100%;
}
</style>
