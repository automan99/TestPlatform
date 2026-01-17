# 测试管理平台 (Test Management Platform)

基于 Vue 3 + Element Plus + Flask-RESTX 的前后端分离测试管理平台。

## 功能特性

### 1. 租户与用户管理
- 多租户支持
- 用户管理（增删改查）
- 项目成员管理

### 2. 项目管理
- 项目创建与配置
- 项目成员管理
- 项目级数据隔离

### 3. 测试用例管理
- 用例的增删改查操作
- 支持测试套件（Suite）分级管理
- 支持用例的各种属性标记（优先级、类型、状态等）
- 用例执行功能
- AI智能执行支持
- 批量操作（删除、移动）

### 4. 测试计划管理
- 测试计划创建与管理
- 支持文件夹分级组织
- 添加测试用例到计划
- 执行测试计划
- 执行记录跟踪
- 分配执行人

### 5. 测试环境管理
- 测试执行主机的增删改查
- 主机状态监控与展示
- 环境资源管理

### 6. 缺陷管理
- 缺陷的增删改查
- 模块化分类管理
- 缺陷属性（严重程度、优先级、状态）
- 缺陷与测试用例/计划关联
- 自定义缺陷工作流

### 7. 测试报告管理
- 测试执行记录
- 基本度量数据统计
- 报告导出

## 技术栈

### 前端
- Vue 3 (Composition API)
- Element Plus
- Vue Router
- Pinia
- Axios
- Vite

### 后端
- Flask
- Flask-RESTX
- SQLAlchemy (ORM)
- Flask-CORS
- Flask-Migrate
- Alembic (数据库迁移)
- MySQL/PostgreSQL

## 项目结构

```
testp/
├── backend/                    # Flask后端
│   ├── app/
│   │   ├── __init__.py        # 应用工厂，自动执行数据库迁移
│   │   ├── config.py          # 配置文件
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── tenant.py      # 租户模型
│   │   │   ├── user.py        # 用户模型
│   │   │   ├── project.py     # 项目模型
│   │   │   ├── test_case.py   # 测试用例模型
│   │   │   ├── test_plan.py   # 测试计划模型
│   │   │   ├── test_env.py    # 测试环境模型
│   │   │   ├── defect.py      # 缺陷模型
│   │   │   └── test_report.py # 测试报告模型
│   │   ├── apis/              # API路由
│   │   │   ├── __init__.py
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── test_case.py
│   │   │   ├── test_plan.py
│   │   │   ├── test_env.py
│   │   │   ├── defect.py
│   │   │   └── test_report.py
│   │   ├── utils/             # 工具函数
│   │   └── middleware/        # 中间件
│   ├── migrations/            # 数据库迁移（自动执行）
│   ├── requirements.txt
│   └── run.py
├── frontend/                   # Vue 3前端
│   ├── src/
│   │   ├── api/               # API调用
│   │   ├── components/        # 公共组件
│   │   ├── views/             # 页面视图
│   │   ├── router/            # 路由配置
│   │   ├── store/             # 状态管理
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 快速开始

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 修改 app/config.py 中的数据库连接配置

# 启动服务（数据库迁移会自动执行）
python run.py
```

后端服务将在 http://localhost:5000 启动

**注意**：应用启动时会自动执行数据库迁移到最新版本，无需手动运行 `flask db upgrade`。

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

## 数据库配置

在 `backend/app/config.py` 中配置数据库连接：

```python
# MySQL
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/test_management'

# PostgreSQL
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/test_management'

# SQLite (开发环境)
SQLALCHEMY_DATABASE_URI = 'sqlite:///test_management.db'
```

## 环境变量

创建 `.env` 文件配置环境变量：

```bash
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

## API文档

后端启动后访问 http://localhost:5000/api/doc 查看Swagger API文档

## 功能截图

### 测试用例管理
- 树形目录结构
- 支持拖拽调整宽度
- 批量操作

### 测试计划管理
- 文件夹组织
- 执行进度跟踪
- 分配执行人

### 缺陷管理
- 模块分类
- 多维度筛选
- 关联测试用例

## 开发计划

- [x] 项目初始化
- [x] 租户与用户管理
- [x] 项目管理
- [x] 测试用例管理
- [x] 测试计划管理
- [x] 测试环境管理
- [x] 缺陷管理
- [x] 测试报告管理
- [x] 数据库自动迁移
- [ ] 自动化测试Agent对接
- [ ] 用户权限管理增强
- [ ] 测试数据导入导出
- [ ] 移动端适配

## 数据库迁移

项目使用 Alembic 进行数据库版本管理。应用启动时会自动执行迁移到最新版本。

如需手动管理迁移：

```bash
# 创建新迁移
flask db migrate -m "描述信息"

# 手动升级到最新版本
flask db upgrade

# 查看当前版本
flask db current

# 回滚迁移
flask db downgrade
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t test-management .

# 运行容器
docker run -p 5000:5000 test-management
```

### 生产环境配置

1. 设置 `FLASK_ENV=production`
2. 使用生产级数据库（MySQL/PostgreSQL）
3. 配置反向代理（Nginx）
4. 设置 `SECRET_KEY` 为强密码
5. 启用 HTTPS

## 常见问题

### 1. 数据库连接失败
检查数据库配置是否正确，确保数据库服务已启动。

### 2. 前端无法连接后端
检查后端服务是否启动，确认 CORS 配置是否正确。

### 3. 迁移执行失败
查看日志获取详细错误信息，确保数据库用户有足够权限。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## License

MIT
