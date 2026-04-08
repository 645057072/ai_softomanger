<template>
  <div class="system-layout">
    <!-- 右侧内容区域 -->
    <div class="system-content">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: 'SystemLayout'
}
</script>

<style scoped>
.system-layout {
  height: 100%;
  background: #f5f7fa;
  position: relative;
}

.system-content {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}
</style>
