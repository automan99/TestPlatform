# 智能测试平台

基于 AI 驱动的新一代自动化测试平台，聚焦 AI 生成测试、AI 执行测试、AI 自动回归、AI 智能分析、AI 自动化修复 Bug 的完整解决方案。

## 功能特性

### 1. AI 测试生成
- 智能分析需求文档和用户故事，自动生成测试用例
- 基于现有代码库推理生成测试场景
- 支持自然语言描述生成测试步骤
- 自动化测试用例优化与覆盖度分析
- 动态生成边界值和异常测试场景

### 2. AI 测试执行
- AI Agent 驱动的自动化测试执行引擎
- 智能识别页面元素和交互行为
- 实时执行状态跟踪与智能重试机制
- 支持多环境并发执行与负载均衡
- 执行日志智能分析与异常根因定位

### 3. AI 自动回归测试
- 智能分析代码变更，自动筛选回归测试集
- 增量测试策略，优化测试执行效率
- 基于风险优先级自动调整回归范围
- 自动检测回退问题，及时预警
- 历史缺陷库智能分析，预防回归风险

### 4. AI 智能分析
- 测试结果多维度智能分析与可视化
- 智能识别测试失败模式与共性缺陷
- 测试质量趋势预测与风险评估
- 代码覆盖率智能分析与优化建议
- 性能瓶颈智能诊断与优化方案

### 5. AI 自动化 Bug 修复
- 智能分析错误日志和堆栈信息
- 自动生成 Bug 修复建议代码
- 修复方案可行性评估与验证
- 自动提交 Pull Request 进行修复
- 修复效果智能验证与回归测试

### 6. MCP (Model Context Protocol) 集成
- 丰富的 MCP 工具生态，扩展 AI 能力边界
- 支持文件系统、数据库、API、Git 等多种工具
- 自定义 MCP 工具开发与集成
- 工具调用链智能编排与优化
- MCP Server 生命周期管理与监控

### 7. AI 技能引擎
- 可编程的 AI 技能/指令集管理
- 支持多种脚本语言（Python、JavaScript、YAML、JSON）
- 技能参数化配置与智能验证
- 技能版本管理与 A/B 测试对比
- 技能执行性能监控与优化

### 8. Git 技能仓库
- 分布式技能代码管理
- 支持 Token、SSH 密钥等多种认证方式
- 手动、定时、Webhook 多种同步策略
- 技能文件变更智能追踪
- 团队协作开发与代码审查流程

### 9. 多租户与企业级管理
- 支持多租户隔离与资源共享
- 细粒度权限管理与角色控制
- OAuth2 第三方登录集成（GitHub、Gitee、GitLab、钉钉）
- 项目级数据隔离与审计日志
- 用户行为分析与操作追溯

## 技术栈

### 前端
- Vue 3 (Composition API) - 响应式前端框架
- Element Plus - 企业级 UI 组件库
- Vue Router - 路由管理
- Pinia - 状态管理
- Axios - HTTP 请求库
- Vite - 现代化构建工具

### 后端
- Flask - 轻量级 Web 框架
- Flask-RESTX - API 文档和 RESTful 框架
- SQLAlchemy - ORM 数据库操作
- Flask-CORS - 跨域请求支持
- Flask-Migrate - 数据库迁移管理
- Alembic - 数据库版本控制
- MySQL/PostgreSQL - 关系型数据库

### AI 能力
- 大语言模型集成 (LLM) - 支持多种 LLM 提供商
- Model Context Protocol (MCP) - AI 工具集成标准协议
- AI Agent 引擎 - 智能测试执行与决策
- 自然语言处理 - 需求理解和测试生成
- 代码分析引擎 - 代码变更影响分析

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

### 前置要求

- Python 3.8+
- Node.js 16+
- MySQL 8.0+ 或 PostgreSQL 12+
- Git

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

# 配置数据库和 AI 模型
# 修改 app/config.py 中的配置
FLASK_ENV=development
SECRET_KEY=your-secret-key
AI_MODEL_API_KEY=your-ai-model-api-key

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
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/ai_test_platform'

# PostgreSQL
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/ai_test_platform'

# SQLite (开发环境)
SQLALCHEMY_DATABASE_URI = 'sqlite:///ai_test_platform.db'
```

## 环境变量

创建 `.env` 文件配置环境变量：

```bash
# 基础配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url

# AI 模型配置
AI_MODEL_PROVIDER=openai
AI_MODEL_API_KEY=your-ai-model-api-key
AI_MODEL_NAME=gpt-4

# MCP 配置
ENABLE_MCP=true
MCP_TIMEOUT=30

# OAuth2 配置
OAUTH_GITHUB_CLIENT_ID=your-github-client-id
OAUTH_GITHUB_CLIENT_SECRET=your-github-client-secret
```

### AI 模型配置

平台支持多种 LLM 提供商，需要在配置中设置相应的 API Key 和模型参数：

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Azure OpenAI
- 本地部署的开源模型 (Llama, Mistral 等)

## API文档

后端启动后访问 http://localhost:5000/api/doc 查看Swagger API文档

## 功能截图

### AI 测试生成
- 智能需求分析与测试用例生成
- 自然语言描述转换为测试步骤
- 自动识别边界值和异常场景
- 测试覆盖度智能分析

### AI 测试执行
- AI Agent 驱动的实时执行展示
- 智能页面元素识别
- 执行日志智能分析
- 异常自动重试机制

### AI 自动回归
- 代码变更影响分析
- 智能筛选回归测试集
- 风险优先级排序
- 回归效率优化

### AI 智能分析
- 测试结果多维度可视化
- 失败模式智能识别
- 质量趋势预测
- 优化建议自动生成

### AI Bug 修复
- 错误日志智能分析
- 自动生成修复代码
- 修复效果验证
- 自动化回归测试

## 开发计划

### 已完成功能
- [x] 项目架构设计
- [x] 多租户与用户管理
- [x] 项目与测试环境管理
- [x] 测试用例管理系统
- [x] 测试计划与执行管理
- [x] 缺陷管理与跟踪
- [x] 测试报告与统计分析
- [x] MCP (Model Context Protocol) 集成
- [x] AI 技能引擎开发
- [x] Git 技能仓库同步
- [x] OAuth2 第三方登录
- [x] AI 测试执行引擎
- [x] 数据库自动迁移

### 正在开发
- [ ] AI 测试生成引擎
- [ ] AI 自动回归测试
- [ ] AI 智能分析平台
- [ ] AI Bug 修复系统

### 规划中功能
- [ ] AI 测试用例优化算法
- [ ] 智能测试覆盖率分析
- [ ] 性能测试智能诊断
- [ ] 多环境并发执行优化
- [ ] 用户权限管理增强（RBAC）
- [ ] 测试数据导入导出优化
- [ ] 移动端适配
- [ ] 实时协作编辑
- [ ] 性能优化和缓存策略
- [ ] 更多 LLM 模型支持
- [ ] 自定义 MCP Server 开发工具

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
docker build -t ai-test-platform .

# 运行容器
docker run -p 5000:5000 \
  -e DATABASE_URL=mysql+pymysql://user:password@db:3306/ai_test_platform \
  -e AI_MODEL_API_KEY=your-api-key \
  -e SECRET_KEY=your-secret-key \
  ai-test-platform
```

### 生产环境配置

1. 设置 `FLASK_ENV=production`
2. 使用生产级数据库（MySQL/PostgreSQL）
3. 配置反向代理（Nginx）
4. 设置 `SECRET_KEY` 为强随机密码
5. 启用 HTTPS
6. 配置 AI 模型 API 限流和重试机制
7. 设置日志级别为 INFO 或 WARNING
8. 配置数据库连接池

### 性能优化建议

- 使用 Redis 缓存 AI 响应结果
- 启用数据库查询缓存
- 配置 CDN 加速静态资源
- 使用队列系统处理 AI 任务
- 启用 GZIP 压缩

## 常见问题

### 1. 数据库连接失败
检查数据库配置是否正确，确保数据库服务已启动，验证数据库用户权限。

### 2. 前端无法连接后端
检查后端服务是否启动，确认 CORS 配置是否正确，验证 API 端点地址。

### 3. AI 模型调用失败
- 验证 API Key 是否正确
- 检查网络连接和代理设置
- 确认 API 配额是否充足
- 查看日志获取详细错误信息

### 4. 迁移执行失败
查看日志获取详细错误信息，确保数据库用户有足够权限。

### 5. MCP Server 连接问题
- 检查 MCP Server 配置是否正确
- 验证传输类型和参数设置
- 查看 MCP 进程日志
- 确认端口号未被占用

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## License

MIT

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至：support@example.com

## 核心技术说明

### AI 测试生成引擎

基于大语言模型的测试用例自动生成系统，通过分析需求文档、用户故事和代码结构，智能生成全面的测试场景：

- **需求理解**：AI 深度理解业务逻辑和功能需求
- **场景推理**：基于领域知识推导出完整的测试路径
- **边界识别**：自动识别边界条件和异常场景
- **用例优化**：持续优化测试用例的覆盖率和有效性

### AI 测试执行引擎

智能化的测试执行引擎，通过 AI Agent 驱动测试流程：

- **智能元素识别**：AI 自动识别页面元素和交互节点
- **自适应执行**：根据页面变化智能调整执行策略
- **智能重试机制**：自动识别失败原因并智能重试
- **异常预测**：提前识别潜在的执行风险

### AI 回归测试系统

基于代码变更分析的智能回归测试系统：

- **变更影响分析**：AI 分析代码变更的影响范围
- **智能筛选**：自动筛选受影响的测试用例
- **风险优先级**：根据代码变更风险调整测试优先级
- **增量回归**：只回归受影响的部分，提高效率

### AI 智能分析平台

全方位的测试数据智能分析与挖掘：

- **模式识别**：AI 识别测试失败的共同模式
- **趋势预测**：预测测试质量趋势和风险
- **根因分析**：智能分析失败的深层原因
- **优化建议**：提供针对性的优化建议

### AI Bug 修复系统

基于代码理解的自动化 Bug 修复系统：

- **日志分析**：AI 智能分析错误日志和堆栈信息
- **修复建议**：自动生成修复代码片段
- **可行性评估**：评估修复方案的可行性和风险
- **自动验证**：自动执行修复验证和回归测试

### MCP (Model Context Protocol)

开放的 AI 工具集成标准协议，扩展 AI 能力边界：

- **工具生态**：连接文件系统、数据库、API 等外部工具
- **智能编排**：AI 自动编排工具调用链
- **标准化接口**：统一的工具调用和管理接口
- **生命周期管理**：完整的工具部署、监控、扩缩容管理

### 技能（Skill）引擎

可编程的 AI 技能管理平台：

- **多种语言**：支持 Python、JavaScript、YAML、JSON
- **参数化配置**：灵活的参数定义和智能验证
- **版本管理**：完整的技能版本控制和 A/B 测试
- **性能监控**：实时的技能执行性能监控和优化

### Git 技能仓库

分布式技能管理和协作平台：

- **代码托管**：基于 Git 的技能代码管理
- **多种认证**：支持 Token、SSH 密钥等多种认证方式
- **智能同步**：手动、定时、Webhook 多种同步策略
- **变更追踪**：完整的技能变更历史和追溯
