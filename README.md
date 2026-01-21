# 测试管理平台 (Test Management Platform)

基于 Vue 3 + Element Plus + Flask-RESTX 的前后端分离测试管理平台。

## 功能特性

### 1. 租户与用户管理
- 多租户支持
- 用户管理（增删改查）
- 项目成员管理
- OAuth2 第三方登录支持（GitHub、Gitee、GitLab、钉钉）

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

### 8. MCP Server 管理
- MCP (Model Context Protocol) Server 注册管理
- 支持 stdio 和 SSE/HTTP 传输类型
- MCP 工具和资源同步
- MCP Server 启用/禁用控制
- 内置和自定义 MCP Server 支持
- MCP 工具调试功能
- 使用统计和执行日志

### 9. 技能（Skill）管理
- AI 技能/指令集管理
- 支持多种脚本类型（Python、JavaScript、YAML、JSON）
- 参数定义和验证
- 技能版本管理
- 使用统计和执行历史

### 10. Git 技能仓库
- Git 仓库技能同步
- 支持多种认证方式（Token、SSH 密钥）
- 手动、定时、Webhook 触发同步
- 同步日志记录和错误处理
- Git 凭证加密存储
- 技能文件变更追踪

### 11. AI 测试执行
- AI Agent 驱动的测试用例执行
- 实时执行状态跟踪
- 执行日志展示
- 支持停止和重新执行
- 执行结果自动保存

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
│   │   │   ├── test_report.py # 测试报告模型
│   │   │   ├── mcp_tool.py    # MCP Server、工具、资源模型
│   │   │   ├── skill.py       # Skill 模型
│   │   │   └── skill_repository.py # Git 技能仓库模型
│   │   ├── apis/              # API路由
│   │   │   ├── __init__.py
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── test_case.py
│   │   │   ├── test_plan.py
│   │   │   ├── test_env.py
│   │   │   ├── defect.py
│   │   │   ├── test_report.py
│   │   │   ├── mcp_skills.py  # MCP Server 和 Skill API
│   │   │   ├── skill_repositories.py # Git 技能仓库 API
│   │   │   ├── oauth.py       # OAuth2 认证 API
│   │   │   └── ai_execution.py # AI 执行 API
│   │   ├── services/          # 服务层
│   │   │   ├── mcp_client.py  # MCP 客户端
│   │   │   ├── mcp_operations.py # MCP 操作
│   │   │   ├── mcp_process_manager.py # MCP 进程管理
│   │   │   └── git_sync_service.py # Git 同步服务
│   │   ├── utils/             # 工具函数
│   │   │   ├── crypto.py      # 加密工具
│   │   │   └── async_helper.py # 异步辅助
│   │   └── middleware/        # 中间件
│   ├── migrations/            # 数据库迁移（自动执行）
│   ├── requirements.txt
│   └── run.py
├── frontend/                   # Vue 3前端
│   ├── src/
│   │   ├── api/               # API调用
│   │   │   ├── mcp-skills.js
│   │   │   ├── skill-repositories.js
│   │   │   ├── oauth.js
│   │   │   └── ai-execution.js
│   │   ├── components/        # 公共组件
│   │   ├── views/             # 页面视图
│   │   │   ├── MCPSkills/     # MCP Server 管理页面
│   │   │   ├── Skills/        # Skill 管理页面
│   │   │   └── TestCase/      # 测试用例和 AI 执行页面
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

# 安装依赖包
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
- [x] MCP Server 集成
- [x] Git 技能仓库同步
- [x] OAuth2 第三方登录
- [x] AI 测试执行
- [ ] 用户权限管理增强（RBAC）
- [ ] 测试数据导入导出
- [ ] 移动端适配
- [ ] 实时协作编辑
- [ ] 性能优化和缓存

## OAuth2 配置

在 `backend/app/config.py` 中配置 OAuth2 提供商：

```python
# GitHub OAuth
OAUTH_GITHUB = {
    'client_id': 'your-github-client-id',
    'client_secret': 'your-github-client-secret'
}

# Gitee OAuth
OAUTH_GITEE = {
    'client_id': 'your-gitee-client-id',
    'client_secret': 'your-gitee-client-secret'
}

# GitLab OAuth
OAUTH_GITLAB = {
    'client_id': 'your-gitlab-client-id',
    'client_secret': 'your-gitlab-client-secret'
}
```

## Git 技能仓库配置

### 1. 创建 Git 凭证

系统支持两种认证方式：

**Token 认证：**
- 适用于 GitHub、Gitee、GitLab
- 需要提供 Personal Access Token
- Token 会被加密存储

**SSH 密钥认证：**
- 适用于所有 Git 仓库
- 需要提供 SSH 私钥内容
- 支持可选的密钥密码

### 2. 创建技能仓库

- 提供 Git 仓库 URL
- 选择分支（默认：main）
- 指定技能文件路径
- 选择认证方式或使用公共仓库

### 3. 配置同步策略

**手动同步：** 需要手动触发同步

**定时同步：** 按配置的时间间隔自动同步

**Webhook 同步：** 通过 Git Webhook 触发同步（需配置 webhook secret）

## MCP Server 配置

### stdio 类型 MCP Server

适用于本地进程启动的 MCP Server：

```json
{
  "name": "Filesystem MCP",
  "code": "filesystem",
  "transport_type": "stdio",
  "command": "npx",
  "arguments": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/directory"],
  "env": {
    "PATH": "/usr/local/bin:/usr/bin:/bin"
  },
  "timeout": 30
}
```

### SSE/HTTP 类型 MCP Server

适用于远程 MCP Server：

```json
{
  "name": "Remote MCP",
  "code": "remote-mcp",
  "transport_type": "sse",
  "url": "https://example.com/mcp/sse",
  "timeout": 30
}
```

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

## 核心技术说明

### MCP (Model Context Protocol)

MCP 是一个开放的标准协议，用于连接 AI 助手与外部工具和数据源。本平台通过以下方式集成 MCP：

- **MCP Server 管理**：注册、配置、监控 MCP Server
- **工具调用**：通过 MCP 调用可用工具
- **资源访问**：通过 MCP 访问外部资源
- **进程管理**：管理 stdio 类型 MCP Server 的生命周期

### 技能（Skill）

技能是封装的测试操作指令集，可以通过 MCP 或直接执行：

- **脚本类型**：Python、JavaScript、YAML、JSON
- **参数化**：支持参数定义和验证
- **版本管理**：记录技能的历史版本
- **Git 同步**：从 Git 仓库自动同步技能文件

### AI 测试执行

AI 测试执行使用 AI Agent 自动化执行测试用例：

- **智能步骤执行**：AI 解析并执行测试步骤
- **实时状态跟踪**：实时反馈执行进度和日志
- **错误处理**：自动识别和处理执行错误
- **结果保存**：自动保存执行结果到报告

## AI开发经验

1. 前端：使用Frontend Design Skills，去https://coolors.co/ 生成配色方案，使用https://www.figma.com/ 设计界面，使用https://www.figma.com/community/plugin/1140011770466815，提示词中控制风格

2. MCP 集成：遵循 MCP 标准协议，支持 stdio 和 SSE 传输类型，实现完整的工具和资源管理

3. Git 同步：使用 GitPython 实现 Git 操作，支持多种认证方式，实现安全的凭证存储

4. OAuth2 认证：实现标准的 OAuth2 授权流程，支持多个主流平台
