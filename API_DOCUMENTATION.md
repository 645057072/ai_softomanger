# 考试系统 API 接口文档

## 文档说明

本文档用于描述考试系统的所有 API 接口，方便第三方系统集成和调用。

**系统版本：** v1.0  
**最后更新：** 2026-04-08  
**基础 URL：** `http://47.93.44.247/api`

---

## 目录

1. [认证接口](#1-认证接口)
2. [用户管理接口](#2-用户管理接口)
3. [组织机构管理接口](#3-组织机构管理接口)
4. [角色管理接口](#4-角色管理接口)
5. [试卷管理接口](#5-试卷管理接口)
6. [题目管理接口](#6-题目管理接口)
7. [考试管理接口](#7-考试管理接口)
8. [成绩管理接口](#8-成绩管理接口)
9. [系统管理接口](#9-系统管理接口)

---

## 通用说明

### 认证方式

所有需要认证的接口都需要在请求头中携带 JWT Token：

```
Authorization: Bearer <access_token>
```

### 响应格式

所有接口统一返回 JSON 格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

**响应码说明：**
- `200`：成功
- `400`：请求参数错误
- `401`：未授权访问
- `403`：禁止访问
- `404`：资源不存在
- `500`：服务器内部错误

---

## 1. 认证接口

### 1.1 用户登录

**接口地址：** `POST /auth/login`

**请求参数：**

```json
{
  "username": "string",
  "password": "string"
}
```

**响应示例：**

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "real_name": "系统管理员",
      "email": "admin@exam.com",
      "role": "admin",
      "status": 1
    }
  }
}
```

### 1.2 用户注册

**接口地址：** `POST /auth/register`

**请求参数：**

```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "real_name": "string",
  "id_card": "string",
  "phone": "string"
}
```

**响应示例：**

```json
{
  "code": 200,
  "message": "注册成功，请等待管理员审核",
  "data": {
    "id": 10,
    "username": "user1",
    "real_name": "张三",
    "email": "user1@example.com",
    "role": "student",
    "status": 0
  }
}
```

### 1.3 刷新 Token

**接口地址：** `POST /auth/refresh`

**请求头：**
```
Authorization: Bearer <refresh_token>
```

**响应示例：**

```json
{
  "code": 200,
  "message": "Token 刷新成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 1.4 用户登出

**接口地址：** `POST /auth/logout`

**请求头：**
```
Authorization: Bearer <access_token>
```

**响应示例：**

```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

### 1.5 获取当前用户信息

**接口地址：** `GET /auth/profile`

**请求头：**
```
Authorization: Bearer <access_token>
```

**响应示例：**

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "username": "admin",
    "real_name": "系统管理员",
    "email": "admin@exam.com",
    "role": "admin",
    "status": 1
  }
}
```

### 1.6 修改密码

**接口地址：** `POST /auth/change-password`

**请求参数：**

```json
{
  "old_password": "string",
  "new_password": "string"
}
```

---

## 2. 用户管理接口

### 2.1 获取待审核用户列表

**接口地址：** `GET /user-management/pending`

**请求参数：**
- `page` (可选): 页码，默认 1
- `per_page` (可选): 每页数量，默认 10
- `inbox` (可选): `unread`（默认）仅未读，`read` 已打开但仍待审核；用于「用户注册审批」左侧分类

### 2.1a 待审核记录标为已读

**接口地址：** `POST /user-management/<user_id>/mark-read`  
**说明**：`status` 仍为 0，仅写入 `registration_read_at`，供「已读消息」列表展示。

**响应示例：**

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "list": [
      {
        "id": 10,
        "username": "user1",
        "real_name": "张三",
        "email": "user1@example.com",
        "phone": "13800138000",
        "id_card": "110101199001011234",
        "role": "student",
        "status": 0,
        "created_at": "2026-04-08T10:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10
  }
}
```

### 2.2 获取所有用户列表

**接口地址：** `GET /user-management/all`

**请求参数：**
- `page` (可选): 页码，默认 1
- `per_page` (可选): 每页数量，默认 10
- `status` (可选): 用户状态 (0:待审核 1:正常 2:禁用)

### 2.3 审核通过用户

**接口地址：** `POST /user-management/<user_id>/approve`

**响应示例：**

```json
{
  "code": 200,
  "message": "审核通过",
  "data": {
    "id": 10,
    "username": "user1",
    "status": 1
  }
}
```

### 2.4 审核退回用户

**接口地址：** `POST /user-management/<user_id>/reject`

### 2.5 删除用户

**接口地址：** `DELETE /user-management/<user_id>`

### 2.6 更新用户信息

**接口地址：** `PUT /user-management/<user_id>`

**请求参数：**

```json
{
  "real_name": "string",
  "email": "string",
  "phone": "string",
  "id_card": "string",
  "role": "string",
  "status": "integer"
}
```

---

## 3. 组织机构管理接口

### 3.1 获取组织机构列表

**接口地址：** `GET /organization`

**请求参数：**
- `page` (可选): 页码，默认 1
- `per_page` (可选): 每页数量，默认 10

**响应示例：**

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "某某科技有限公司",
        "tax_id": "91110108MA01234567",
        "address": "北京市海淀区某某路 1 号",
        "phone": "010-12345678",
        "legal_representative": "李四",
        "registration_date": "2020-01-01",
        "industry": "信息技术",
        "status": 1
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10
  }
}
```

### 3.2 获取组织机构详情

**接口地址：** `GET /organization/<org_id>`

### 3.3 创建组织机构

**接口地址：** `POST /organization`

**请求参数：**

```json
{
  "name": "string",
  "tax_id": "string",
  "address": "string",
  "phone": "string",
  "legal_representative": "string",
  "registration_date": "YYYY-MM-DD",
  "industry": "string"
}
```

**必填字段：** `name`

### 3.4 更新组织机构

**接口地址：** `PUT /organization/<org_id>`

### 3.5 删除组织机构

**接口地址：** `DELETE /organization/<org_id>`

---

## 4. 角色管理接口

### 4.1 获取角色列表

**接口地址：** `GET /role`

**请求参数：**
- `page` (可选): 页码，默认 1
- `per_page` (可选): 每页数量，默认 10

**响应示例：**

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "admin",
        "description": "系统管理员",
        "status": 1
      }
    ],
    "total": 3,
    "page": 1,
    "per_page": 10
  }
}
```

### 4.2 创建角色

**接口地址：** `POST /role`

**请求参数：**

```json
{
  "name": "string",
  "description": "string"
}
```

### 4.3 更新角色

**接口地址：** `PUT /role/<role_id>`

### 4.4 删除角色

**接口地址：** `DELETE /role/<role_id>`

---

## 5. 试卷管理接口

### 5.1 获取试卷列表

**接口地址：** `GET /paper`

**请求参数：**
- `page` (可选): 页码，默认 1
- `per_page` (可选): 每页数量，默认 10
- `exam_type_id` (可选): 试卷类型 ID
- `exam_subject_id` (可选): 科目 ID
- `status` (可选): 状态 (0:草稿 1:已发布 2:已结束)

**响应示例：**

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "list": [
      {
        "id": 1,
        "title": "2026 年期末考试试卷",
        "description": "期末考试用卷",
        "exam_type_id": 1,
        "exam_subject_id": 1,
        "total_score": 100.0,
        "duration": 120,
        "status": 1
      }
    ],
    "total": 10,
    "page": 1,
    "per_page": 10
  }
}
```

### 5.2 获取试卷详情

**接口地址：** `GET /paper/<paper_id>`

### 5.3 创建试卷

**接口地址：** `POST /paper`

### 5.4 更新试卷

**接口地址：** `PUT /paper/<paper_id>`

### 5.5 删除试卷

**接口地址：** `DELETE /paper/<paper_id>`

---

## 6. 题目管理接口

### 6.1 获取题目列表

**接口地址：** `GET /question`

**请求参数：**
- `page` (可选): 页码，默认 1
- `per_page` (可选): 每页数量，默认 10
- `exam_type_id` (可选): 试卷类型 ID
- `exam_subject_id` (可选): 科目 ID
- `question_type` (可选): 题目类型 (single_choice, multiple_choice, judgment, fill_blank)

### 6.2 获取题目详情

**接口地址：** `GET /question/<question_id>`

### 6.3 创建题目

**接口地址：** `POST /question`

### 6.4 更新题目

**接口地址：** `PUT /question/<question_id>`

### 6.5 删除题目

**接口地址：** `DELETE /question/<question_id>`

---

## 7. 考试管理接口

### 7.1 获取考试记录列表

**接口地址：** `GET /exam`

### 7.2 开始考试

**接口地址：** `POST /exam/start`

**请求参数：**

```json
{
  "paper_id": "integer"
}
```

### 7.3 提交考试

**接口地址：** `POST /exam/submit`

**请求参数：**

```json
{
  "exam_id": "integer",
  "answers": [
    {
      "question_id": 1,
      "answer": "A"
    }
  ]
}
```

---

## 8. 成绩管理接口

### 8.1 获取成绩列表

**接口地址：** `GET /score`

### 8.2 获取成绩详情

**接口地址：** `GET /score/<exam_id>`

---

## 9. 系统管理接口

### 9.1 获取系统日志

**接口地址：** `GET /system/logs`

### 9.2 获取系统配置

**接口地址：** `GET /system/configs`

### 9.3 更新系统配置

**接口地址：** `PUT /system/configs/<config_key>`

---

## 10. 数据管理扩展接口（管理员）

**说明**：均需 `Authorization: Bearer <token>`，且当前用户角色为 `admin`。

### 10.1 用户管理 - 已审核通过列表

**接口地址：** `GET /user-management/approved`  
**查询参数：** `page`、`per_page`  
**说明**：列出已审核通过且角色非管理员的用户（常用于统计或扩展）；「用户注册审批」中「已读/未读」待审列表请使用 `GET /user-management/pending` 的 `inbox` 参数。

### 10.2 在线用户

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/online-users` | 分页列表；查询参数 `page`、`per_page`、`username`（可选，模糊） |
| GET | `/online-users/<id>` | 单条详情 |
| POST | `/online-users` | 创建在线记录（JSON：`user_id` 必填；`username`、`ip_address`、`status` 可选）；同一 `user_id` 仅保留一条 |
| DELETE | `/online-users/<id>` | 删除在线记录（强制下线） |
| PUT | `/online-users/<id>` | 更新状态等（JSON：`status`） |

### 10.3 业务操作日志

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/biz-operation-logs` | 分页；`username`、`op_status` 可选 |
| GET | `/biz-operation-logs/<id>` | 详情 |
| POST | `/biz-operation-logs` | 创建（JSON：`description`、`op_status`、`failure_detail` 可选） |
| PUT | `/biz-operation-logs/<id>` | 更新 |
| DELETE | `/biz-operation-logs/<id>` | 删除 |

### 10.4 数据备份

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/data-backup` | 备份文件列表（`uploads/backups` 下 `.db`） |
| POST | `/data-backup` | 执行一次 SQLite 库文件备份 |
| DELETE | `/data-backup?filename=xxx.db` | 删除指定备份文件 |

### 10.5 数据恢复

**接口地址：** `POST /data-restore`  
**请求体 JSON：** `{ "filename": "exam_backup_xxx.db" }`  
**说明**：用指定备份覆盖当前 SQLite 数据库文件；部署环境下需重启后端进程。

---

## 附录

### A. 数据字典

#### 用户状态 (status)
- `0`: 待审核
- `1`: 正常
- `2`: 禁用

#### 角色类型 (role)
- `student`: 学生
- `teacher`: 教师
- `admin`: 管理员

#### 题目类型 (question_type)
- `single_choice`: 单选题
- `multiple_choice`: 多选题
- `judgment`: 判断题
- `fill_blank`: 填空题

#### 试卷状态 (status)
- `0`: 草稿
- `1`: 已发布
- `2`: 已结束

#### 考试状态 (status)
- `0`: 进行中
- `1`: 已提交
- `2`: 已批改

### B. 管理员权限说明

- 用户表字段 `role = admin` 的账号在系统中拥有全部业务管理、系统设置、数据管理等菜单与接口权限。
- 前端侧栏与路由通过 `requiresAdmin` 与 `userStore.isAdmin` 控制；后端各管理类接口统一校验 `User.role == 'admin'`。
- 角色表、菜单表、角色菜单关联表可用于非管理员用户的扩展授权；**管理员不依赖上述表即可使用全部功能**。

### C. 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权访问 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

### D. 联系方式

**技术支持：** exam-system-support@example.com  
**文档版本：** v1.0

---

**注意：** 本文档为考试系统标准 API 接口文档，第三方系统集成时请参考本文档进行开发。
