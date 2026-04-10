# 考试系统数据库设计文档

## 数据库概述

- **数据库类型**: MySQL 8.0（Docker 服务名 `db`，数据卷 `mysql_data`）
- **连接**: 容器内 `MYSQL_HOST=db`，或由 `DATABASE_URL=mysql+pymysql://...@db:3306/exam_system?charset=utf8mb4`
- **创建时间**: 2026-04-08
- **最后更新**: 2026-04-10

## 数据表字典

### 1. users - 用户表

**说明**: 存储系统用户信息

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| username | VARCHAR | 50 | 否 | - | 用户名，唯一 |
| password_hash | VARCHAR | 255 | 否 | - | 密码哈希 |
| real_name | VARCHAR | 50 | 是 | NULL | 真实姓名 |
| email | VARCHAR | 100 | 是 | NULL | 电子邮箱 |
| phone | VARCHAR | 20 | 是 | NULL | 手机号码 |
| id_card | VARCHAR | 18 | 是 | NULL | 身份证号 |
| role | VARCHAR | 20 | 否 | student | 角色：admin, teacher, student |
| status | INTEGER | - | 否 | 1 | 状态：0 待审核，1 正常，2 禁用 |
| registration_read_at | DATETIME | - | 是 | NULL | 用户注册审批：管理员是否已打开过待审核记录（未读/已读分类） |
| avatar | VARCHAR | 255 | 是 | NULL | 头像 URL |
| last_login | DATETIME | - | 是 | NULL | 最后登录时间 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY (id)
- UNIQUE (username)

---

### 2. organizations - 组织机构表

**说明**: 存储组织机构信息

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| name | VARCHAR | 100 | 否 | - | 机构名称 |
| code | VARCHAR | 50 | 是 | NULL | 机构代码 |
| parent_id | INTEGER | - | 是 | NULL | 父机构 ID |
| level | INTEGER | - | 否 | 1 | 机构层级 |
| type | VARCHAR | 20 | 是 | NULL | 机构类型 |
| address | VARCHAR | 255 | 是 | NULL | 联系地址 |
| contact | VARCHAR | 50 | 是 | NULL | 联系人 |
| phone | VARCHAR | 20 | 是 | NULL | 联系电话 |
| email | VARCHAR | 100 | 是 | NULL | 联系邮箱 |
| status | INTEGER | - | 否 | 1 | 状态：0 禁用，1 启用 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY (id)
- INDEX (parent_id)
- INDEX (code)

---

### 3. roles - 角色表

**说明**: 存储系统角色信息

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| name | VARCHAR | 50 | 否 | - | 角色名称 |
| code | VARCHAR | 50 | 否 | - | 角色代码，唯一 |
| description | TEXT | - | 是 | NULL | 角色描述 |
| status | INTEGER | - | 否 | 1 | 状态：0 禁用，1 启用 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY (id)
- UNIQUE (code)

---

### 4. menus - 菜单表

**说明**: 存储系统菜单信息

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| name | VARCHAR | 50 | 否 | - | 菜单名称 |
| path | VARCHAR | 255 | 否 | - | 菜单路径 |
| icon | VARCHAR | 50 | 是 | NULL | 菜单图标 |
| parent_id | INTEGER | - | 是 | NULL | 父菜单 ID |
| sort_order | INTEGER | - | 否 | 0 | 排序顺序 |
| type | VARCHAR | 20 | 否 | menu | 类型：menu, button |
| permission | VARCHAR | 100 | 是 | NULL | 权限标识 |
| status | INTEGER | - | 否 | 1 | 状态：0 禁用，1 启用 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY (id)
- INDEX (parent_id)

---

### 5. role_menu - 角色菜单关联表

**说明**: 存储角色与菜单的关联关系

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| role_id | INTEGER | - | 否 | - | 角色 ID |
| menu_id | INTEGER | - | 否 | - | 菜单 ID |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**索引**:
- PRIMARY KEY (id)
- INDEX (role_id)
- INDEX (menu_id)
- UNIQUE (role_id, menu_id)

---

### 6. exam_types - 考试类型表

**说明**: 存储考试分类信息

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| name | VARCHAR | 100 | 否 | - | 类型名称 |
| code | VARCHAR | 50 | 否 | - | 类型代码，唯一 |
| description | TEXT | - | 是 | NULL | 类型描述 |
| sort_order | INTEGER | - | 否 | 0 | 排序顺序 |
| status | INTEGER | - | 否 | 1 | 状态：0 禁用，1 启用 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY (id)
- UNIQUE (code)

---

### 7. exam_subjects - 考试科目表

**说明**: 存储考试科目信息

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| name | VARCHAR | 100 | 否 | - | 科目名称 |
| code | VARCHAR | 50 | 否 | - | 科目代码，唯一 |
| type_id | INTEGER | - | 是 | NULL | 考试类型 ID |
| description | TEXT | - | 是 | NULL | 科目描述 |
| sort_order | INTEGER | - | 否 | 0 | 排序顺序 |
| status | INTEGER | - | 否 | 1 | 状态：0 禁用，1 启用 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY (id)
- UNIQUE (code)
- INDEX (type_id)

---

### 8. questions - 题库表

**说明**: 存储试题信息

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| subject_id | INTEGER | - | 否 | - | 科目 ID |
| type | VARCHAR | 20 | 否 | - | 题型：single_choice, multiple_choice, judgment |
| content | TEXT | - | 否 | - | 题目内容 |
| options | TEXT | - | 是 | NULL | 选项（JSON 格式） |
| answer | VARCHAR | 255 | 否 | - | 正确答案 |
| analysis | TEXT | - | 是 | NULL | 答案解析 |
| difficulty | VARCHAR | 20 | 是 | medium | 难度：easy, medium, hard |
| score | DECIMAL | 5,2 | 否 | 1.0 | 默认分值 |
| status | INTEGER | - | 否 | 1 | 状态：0 禁用，1 启用 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY (id)
- INDEX (subject_id)
- INDEX (type)
- INDEX (difficulty)

---

### 9. papers - 试卷表

**说明**: 存储试卷信息

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| name | VARCHAR | 100 | 否 | - | 试卷名称 |
| subject_id | INTEGER | - | 否 | - | 科目 ID |
| type | VARCHAR | 20 | 否 | manual | 组卷方式：manual, auto |
| total_score | DECIMAL | 5,2 | 否 | 100.0 | 总分 |
| pass_score | DECIMAL | 5,2 | 否 | 60.0 | 及格分 |
| duration | INTEGER | - | 否 | 120 | 考试时长（分钟） |
| status | INTEGER | - | 否 | 0 | 状态：0 草稿，1 发布，2 停用 |
| created_by | INTEGER | - | 否 | - | 创建人 ID |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY (id)
- INDEX (subject_id)
- INDEX (created_by)

---

### 10. paper_questions - 试卷试题关联表

**说明**: 存储试卷与试题的关联关系

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| paper_id | INTEGER | - | 否 | - | 试卷 ID |
| question_id | INTEGER | - | 否 | - | 试题 ID |
| score | DECIMAL | 5,2 | 否 | - | 本题分值 |
| sort_order | INTEGER | - | 否 | 0 | 题目顺序 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**索引**:
- PRIMARY KEY (id)
- INDEX (paper_id)
- INDEX (question_id)
- UNIQUE (paper_id, question_id)

---

### 11. exams - 考试表

**说明**: 存储考试安排信息

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| name | VARCHAR | 100 | 否 | - | 考试名称 |
| paper_id | INTEGER | - | 否 | - | 试卷 ID |
| start_time | DATETIME | - | 否 | - | 开始时间 |
| end_time | DATETIME | - | 否 | - | 结束时间 |
| max_students | INTEGER | - | 是 | NULL | 最大考生人数 |
| status | INTEGER | - | 否 | 0 | 状态：0 未开始，1 进行中，2 已结束 |
| created_by | INTEGER | - | 否 | - | 创建人 ID |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY (id)
- INDEX (paper_id)
- INDEX (start_time)
- INDEX (status)

---

### 12. exam_answers - 考试答案表

**说明**: 存储考生提交的答案

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| exam_id | INTEGER | - | 否 | - | 考试 ID |
| user_id | INTEGER | - | 否 | - | 用户 ID |
| question_id | INTEGER | - | 否 | - | 试题 ID |
| answer | VARCHAR | 255 | 否 | - | 用户答案 |
| is_correct | INTEGER | - | 是 | NULL | 是否正确：0 错误，1 正确 |
| score | DECIMAL | 5,2 | 是 | 0 | 得分 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 答题时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY (id)
- INDEX (exam_id)
- INDEX (user_id)
- INDEX (question_id)
- UNIQUE (exam_id, user_id, question_id)

---

### 13. exam_logs - 考试日志表

**说明**: 存储考试过程日志

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| exam_id | INTEGER | - | 否 | - | 考试 ID |
| user_id | INTEGER | - | 否 | - | 用户 ID |
| action | VARCHAR | 50 | 否 | - | 操作：start, submit, auto_submit |
| ip_address | VARCHAR | 50 | 是 | NULL | IP 地址 |
| user_agent | VARCHAR | 255 | 是 | NULL | 浏览器信息 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 操作时间 |

**索引**:
- PRIMARY KEY (id)
- INDEX (exam_id)
- INDEX (user_id)
- INDEX (action)

---

### 14. system_logs - 系统日志表

**说明**: 存储系统操作日志

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| user_id | INTEGER | - | 是 | NULL | 用户 ID |
| module | VARCHAR | 50 | 是 | NULL | 模块名称 |
| action | VARCHAR | 100 | 否 | - | 操作行为 |
| ip_address | VARCHAR | 50 | 是 | NULL | IP 地址 |
| status | INTEGER | - | 否 | 1 | 状态：0 失败，1 成功 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 操作时间 |

**索引**:
- PRIMARY KEY (id)
- INDEX (user_id)
- INDEX (module)
- INDEX (created_at)

---

### 15. system_configs - 系统配置表

**说明**: 存储系统配置信息

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| config_key | VARCHAR | 100 | 否 | - | 配置键，唯一 |
| config_value | TEXT | - | 是 | NULL | 配置值 |
| config_type | VARCHAR | 20 | 是 | string | 配置类型：string, number, boolean, json |
| description | VARCHAR | 255 | 是 | NULL | 配置说明 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY (id)
- UNIQUE (config_key)

---

### 16. user_roles - 用户角色关联表

**说明**: 存储用户与角色的关联关系

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| user_id | INTEGER | - | 否 | - | 用户 ID |
| role_id | INTEGER | - | 否 | - | 角色 ID |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**索引**:
- PRIMARY KEY (id)
- INDEX (user_id)
- INDEX (role_id)
- UNIQUE (user_id, role_id)

---

### 17. user_organizations - 用户组织机构关联表

**说明**: 存储用户与组织机构的关联关系

| 字段名 | 类型 | 长度 | 允许 NULL | 默认值 | 说明 |
|--------|------|------|---------|--------|------|
| id | INTEGER | - | 否 | - | 主键，自增 |
| user_id | INTEGER | - | 否 | - | 用户 ID |
| organization_id | INTEGER | - | 否 | - | 组织机构 ID |
| is_primary | INTEGER | - | 否 | 0 | 是否主机构：0 否，1 是 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**索引**:
- PRIMARY KEY (id)
- INDEX (user_id)
- INDEX (organization_id)
- UNIQUE (user_id, organization_id)

---

## 数据库关系图

```
users ─┬─< user_roles >─ roles
       ├─< user_organizations >─ organizations
       ├─< system_logs
       ├─< exam_logs
       ├─< exam_answers
       └─< exams (created_by)

organizations ─┬─< user_organizations
               └─< organizations (parent_id)

roles ─┬─< user_roles
       └─< role_menu >─ menus

menus ─┬─< role_menu
       └─< menus (parent_id)

exam_types ─< exam_subjects

exam_subjects ─┬─< questions
               └─< papers

questions ─┬─< paper_questions
           └─< exam_answers

papers ─┬─< paper_questions
        └─< exams

exams ─┬─< exam_logs
       └─< exam_answers
```

---

### online_users - 在线用户表

**说明**：用户登录成功后写入一条记录（同一用户仅保留一条）；调用登出接口或管理员「下线」时删除。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户 ID，唯一，外键 users.id |
| username | VARCHAR(50) | 用户名 |
| ip_address | VARCHAR(50) | IP |
| login_time | DATETIME | 登录时间 |
| status | VARCHAR(20) | 如：在线 |

---

### biz_operation_logs - 业务操作日志表

**说明**：数据管理「日志」模块展示；注册提交、审核等写入；`op_status` 为「失败」时 `failure_detail` 存详细错误信息。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户 ID，可空 |
| username | VARCHAR(50) | 用户名 |
| ip_address | VARCHAR(50) | IP |
| description | VARCHAR(100) | 操作说明（≤100 字） |
| op_status | VARCHAR(20) | 提交、审核、失败 |
| failure_detail | TEXT | 失败详情（如异常栈） |
| created_at | DATETIME | 创建时间 |

---

## 数据库初始化说明

### 1. 自动创建表

系统启动时会自动执行 `db.create_all()` 创建所有数据库表。

### 2. 初始化管理员账户

系统启动时会自动检查并创建管理员账户：
- 用户名：admin
- 密码：admin123
- 角色：admin

### 3. 数据库备份

建议定期备份：使用管理端「数据备份」生成 `.sql`，或宿主机执行 `mysqldump` 导出到安全位置。

---

## 版本历史

| 版本 | 日期 | 说明 | 作者 |
|------|------|------|------|
| 1.0 | 2026-04-08 | 初始版本，包含所有基础表 | 系统自动生成 |

---

## 注意事项

1. 所有时间字段使用 UTC 时间
2. 密码使用 bcrypt 或类似算法加密存储
3. 敏感数据（如身份证号）建议加密存储
4. 定期清理过期日志数据
5. 生产环境建议使用 MySQL 或 PostgreSQL
