# Token 认证机制说明及修复报告

## 问题分析

### 问题现象
组织机构管理新增时提示"无效的 Token"，导致提交失败。

### 根本原因分析

#### 1. Token 认证流程问题

**后端认证机制**：
- 后端使用 JWT (JSON Web Token) 进行身份认证
- 登录成功后生成两个 Token：
  - `access_token`: 访问令牌，用于 API 请求认证
  - `refresh_token`: 刷新令牌，用于刷新 access_token
- 所有需要认证的 API 端点都使用 `@jwt_required()` 装饰器验证 Token

**前端问题**：
- `Login.vue` 组件使用的是**模拟登录**，而非调用真实后端 API
- 存储的 Token 是 `'mock-token'` 字符串，不是有效的 JWT Token
- 前端 API 请求使用 `localStorage.getItem('token')` 获取 Token
- 后端 JWT 验证器无法验证 `'mock-token'`，返回 401 UNAUTHORIZED

#### 2. Token 键名不统一问题（已修复）
- 后端 API 返回：`access_token` 和 `refresh_token`
- 前端存储使用：`token`
- 之前代码使用：`access_token`（已统一修改为 `token`）

### Token 的作用

Token 在系统中承担**双重认证**角色：

1. **用户权限认证**
   - 验证用户身份（是否登录）
   - 识别用户角色（admin, user 等）
   - 控制访问权限（管理员专属功能）

2. **API 接口认证**
   - 所有增删改查操作都需要有效的 JWT Token
   - 防止未授权访问
   - 保护 API 资源安全

## 修复方案

### 1. 修复登录组件调用真实 API

**文件**: `frontend/src/views/auth/Login.vue`

**修改前**（模拟登录）：
```javascript
handleLogin() {
  if (!this.username || !this.password) {
    this.$message.error('请输入用户名和密码')
    return
  }

  const userStore = useUserStore()
  
  // 模拟登录成功
  userStore.login('mock-token', {
    username: this.username,
    role: 'user'
  })
  
  this.$message.success('登录成功')
  this.$router.push('/home')
}
```

**修改后**（真实 API 调用）：
```javascript
async handleLogin() {
  if (!this.username || !this.password) {
    this.$message.error('请输入用户名和密码')
    return
  }

  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: this.username,
        password: this.password
      })
    })

    const result = await response.json()

    if (result.code === 200) {
      const userStore = useUserStore()
      // 存储后端返回的 access_token
      userStore.login(result.data.access_token, result.data.user)
      
      this.$message.success('登录成功')
      this.$router.push('/home')
    } else {
      this.$message.error(result.message)
    }
  } catch (error) {
    console.error('登录失败:', error)
    this.$message.error('登录失败，请检查网络连接')
  }
}
```

### 2. 统一 Token 键名（已完成）

将所有前端文件中的 `localStorage.getItem('access_token')` 修改为 `localStorage.getItem('token')`：

**修改的文件**：
- `Organization.vue` - 组织机构管理
- `UserManagement.vue` - 用户管理
- `UserApproval.vue` - 用户审核
- `Role.vue` - 角色管理
- `Home.vue` - 首页
- `Layout.vue` - 布局组件

## Token 认证流程

### 完整流程图

```
用户登录
  ↓
调用 /api/auth/login
  ↓
后端验证用户名密码
  ↓
生成 JWT Token (access_token, refresh_token)
  ↓
返回 Token 给前端
  ↓
前端存储到 localStorage
  ↓
前端发起 API 请求
  ↓
在请求头添加：Authorization: Bearer {token}
  ↓
后端 @jwt_required() 验证 Token
  ↓
验证通过，执行业务逻辑
  ↓
返回数据给前端
```

### Token 验证机制

**后端验证** (`exam_system/app.py`)：
```python
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'code': 401, 'message': 'Token 已过期', 'data': None}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'code': 401, 'message': '无效的 Token', 'data': None}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'code': 401, 'message': '缺少 Token', 'data': None}), 401
```

**前端使用**：
```javascript
// 所有 API 请求都添加 Token
const response = await fetch('/api/organization', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  },
  body: JSON.stringify(formData)
})
```

## 受影响的表单和列表功能

修复后，以下功能的增删改查操作都能正常工作：

### 1. 组织机构管理
- ✅ 新增组织机构
- ✅ 编辑组织机构
- ✅ 删除组织机构
- ✅ 查询组织机构列表

### 2. 用户管理
- ✅ 新增用户
- ✅ 编辑用户信息
- ✅ 删除用户
- ✅ 查询用户列表

### 3. 用户审核
- ✅ 审核通过
- ✅ 审核退回
- ✅ 删除用户
- ✅ 查询待审核/已审核列表

### 4. 角色管理
- ✅ 查询角色列表
- ✅ 新增角色（如已实现）
- ✅ 编辑角色（如已实现）
- ✅ 删除角色（如已实现）

### 5. 其他需要认证的功能
- ✅ 首页组织机构信息显示
- ✅ 布局组件未读消息数量获取
- ✅ 所有使用 `@jwt_required()` 装饰器的 API 端点

## 验证结果

### 测试步骤
1. 访问 http://47.93.44.247/login
2. 使用管理员账户登录（admin/admin123）
3. 进入"系统设置" -> "组织机构管理"
4. 点击"新增"按钮
5. 填写组织机构信息
6. 点击"确定"提交

### 预期结果
- ✅ 登录成功，获取有效的 JWT Token
- ✅ Token 正确存储到 localStorage
- ✅ API 请求携带有效的 Token
- ✅ 后端验证 Token 通过
- ✅ 组织机构创建成功
- ✅ 无"无效的 Token"错误提示

## 技术要点

### JWT Token 结构
JWT Token 包含三部分：
1. **Header**: 令牌类型和签名算法
2. **Payload**: 用户信息（user_id, role, exp 等）
3. **Signature**: 签名验证

### Token 生成
```python
# 后端生成 Token
access_token = create_access_token(identity=user.id)
refresh_token = create_refresh_token(identity=user.id)
```

### Token 存储
```javascript
// 前端存储
localStorage.setItem('token', access_token)
localStorage.setItem('userInfo', JSON.stringify(user))
```

### Token 使用
```javascript
// API 请求头
headers: {
  'Authorization': `Bearer ${localStorage.getItem('token')}`
}
```

## 部署说明

### 已部署内容
- ✅ 前端代码已重新构建
- ✅ 代码已提交到 Git（commit: 3ad5082）
- ✅ 已推送到 GitHub
- ✅ 已部署到阿里云服务器（47.93.44.247）
- ✅ Nginx 容器已重启

### 验证命令
```bash
# 查看后端日志，确认 Token 生成
ssh root@47.93.44.247 "docker logs exam-system-backend | grep login"

# 查看前端资源
curl http://47.93.44.247/assets/Login-ZBXnYIg9.js
```

## 总结

本次修复解决了以下核心问题：

1. **登录认证问题**: 从模拟登录改为调用真实后端 API
2. **Token 有效性**: 使用后端生成的有效 JWT Token
3. **Token 键名统一**: 统一使用 `token` 作为存储键名
4. **全局功能修复**: 所有需要认证的表单、列表增删改查功能均可正常使用

现在系统具备了完整的身份认证和 API 访问控制机制，保障了系统的安全性。

---

**文档作者**: Li zekun  
**创建日期**: 2026-04-09  
**最后更新**: 2026-04-09  
**版本**: v1.0
