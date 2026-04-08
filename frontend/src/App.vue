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
      <router-view name="auth" />
    </template>
  </div>
</template>

<script>
import Layout from './components/Layout.vue'

export default {
  name: 'App',
  components: {
    Layout
  },
  computed: {
    isLoggedIn() {
      return !!this.$store.state.user.token
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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f7fa;
  color: #333;
}

#app {
  min-height: 100vh;
}
</style>
