<template>
  <div class="page-wrap">
    <el-card>
      <template #header>
        <span>数据恢复</span>
      </template>
      <el-alert
        title="将从 .sql 备份导入当前 MySQL 数据库，操作后建议重启后端服务。仅限管理员。"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      />
      <el-form label-width="120px" @submit.prevent>
        <el-form-item label="备份文件名">
          <el-select v-model="filename" filterable placeholder="请选择备份文件" style="width: 100%; max-width: 400px">
            <el-option v-for="f in files" :key="f.filename" :label="f.filename" :value="f.filename" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="danger" :loading="loading" @click="handleRestore">执行恢复</el-button>
          <el-button @click="loadFiles">刷新列表</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dataBackupApi, dataRestoreApi } from '../../api'

export default {
  name: 'DataRestorePage',
  setup() {
    const files = ref([])
    const filename = ref('')
    const loading = ref(false)

    const loadFiles = async () => {
      try {
        const result = await dataBackupApi.list()
        if (result.code === 200) {
          files.value = result.data.list || []
          if (!filename.value && files.value.length) {
            filename.value = files.value[0].filename
          }
        }
      } catch (e) {
        const m = e?.response?.data?.message
        ElMessage.error(m || '获取备份列表失败')
      }
    }

    const handleRestore = () => {
      if (!filename.value) {
        ElMessage.warning('请选择备份文件')
        return
      }
      ElMessageBox.confirm(
        '确认用该备份覆盖当前数据库？此操作不可逆。',
        '危险操作',
        { type: 'warning' }
      ).then(async () => {
        loading.value = true
        try {
          const result = await dataRestoreApi.restore({ filename: filename.value })
          if (result.code === 200) {
            ElMessage.success(result.message || '已执行恢复')
          } else {
            ElMessage.error(result.message || '恢复失败')
          }
        } catch (e) {
          const m = e?.response?.data?.message
          ElMessage.error(m || '恢复失败')
        } finally {
          loading.value = false
        }
      }).catch(() => {})
    }

    onMounted(() => {
      loadFiles()
    })

    return { files, filename, loading, loadFiles, handleRestore }
  }
}
</script>

<style scoped>
.page-wrap {
  padding: 16px;
}
</style>
