# 测试管理平台 (Test Management Platform)

基于 Vue 3 + Element Plus + Flask-RESTX 的前后端分离测试管理平台。

## 功能特性

### 1. 测试用例管理
- 用例的增删改查操作
- 支持文件夹分级管理
- 支持用例的各种属性标记（优先级、类型、状态等）

### 2. 测试计划/任务
- 新建测试计划
- 添加测试用例到测试计划
- 执行测试计划
- 预留自动化执行Agent对接接口

### 3. 测试环境管理
- 测试执行主机的增删改查
- 主机状态监控与展示
- 资源管理

### 4. 缺陷管理
- 缺陷的增删改查
- 自定义缺陷状态流程
- 缺陷与测试用例/计划关联

### 5. 测试报告管理
- 测试执行记录
- 基本度量数据统计
- 报告导出

## 技术栈

### 前端
- Vue 3
- Element Plus
- Vue Router
- Pinia
- Axios
- Vite

### 后端
- Flask
- Flask-RESTX
- SQLAlchemy
- Flask-CORS
- Flask-Migrate
- MySQL/PostgreSQL

## 项目结构

```
test-management-platform/
├── backend/                    # Flask后端
│   ├── app/
│   │   ├── __init__.py        # 应用初始化
│   │   ├── config.py          # 配置文件
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── test_case.py
│   │   │   ├── test_plan.py
│   │   │   ├── test_env.py
│   │   │   ├── defect.py
│   │   │   └── test_report.py
│   │   ├── apis/              # API路由
│   │   │   ├── __init__.py
│   │   │   ├── test_case.py
│   │   │   ├── test_plan.py
│   │   │   ├── test_env.py
│   │   │   ├── defect.py
│   │   │   └── test_report.py
│   │   └── utils/             # 工具函数
│   ├── migrations/            # 数据库迁移
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
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 修改 app/config.py 中的数据库连接配置

# 初始化数据库
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 启动服务
python run.py
```

后端服务将在 http://localhost:5000 启动

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

## API文档

后端启动后访问 http://localhost:5000/api/doc 查看Swagger API文档

## 数据库配置

在 `backend/app/config.py` 中配置数据库连接：

```python
# MySQL
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/test_management'

# PostgreSQL
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/test_management'
```

## 开发计划

- [x] 项目初始化
- [x] 测试用例管理
- [x] 测试计划管理
- [x] 测试环境管理
- [x] 缺陷管理
- [x] 测试报告管理
- [ ] 自动化测试Agent对接
- [ ] 用户权限管理
- [ ] 测试数据导入导出

## License

MIT
