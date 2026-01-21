"""
MCP Server 模型 - Model Context Protocol 服务器
"""
from datetime import datetime
from app import db


class MCPServer(db.Model):
    """MCP Server模型"""
    __tablename__ = 'mcp_servers'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True, comment='租户ID')

    # 基础信息
    name = db.Column(db.String(200), nullable=False, comment='服务器名称')
    code = db.Column(db.String(50), unique=True, index=True, comment='服务器代码')

    # 传输类型
    transport_type = db.Column(db.String(20), default='stdio', comment='传输类型: stdio, sse, http')

    # 命令配置（用于 stdio 类型）
    command = db.Column(db.String(500), comment='执行命令，如 npx, python, /path/to/server')
    arguments = db.Column(db.Text, comment='JSON数组格式的参数，如 ["--port", "3000"]')
    env = db.Column(db.Text, comment='JSON对象格式的环境变量，如 {"API_KEY": "xxx"}')

    # 连接配置（用于 sse/http 类型）
    url = db.Column(db.String(500), comment='SSE/HTTP 端点URL')

    # 超时配置
    timeout = db.Column(db.Integer, default=30, comment='超时时间（秒）')

    # 状态管理
    status = db.Column(db.String(20), default='active', comment='状态: active, inactive, error')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    is_builtin = db.Column(db.Boolean, default=False, comment='是否为内置MCP Server')

    # 元数据
    tags = db.Column(db.String(500), comment='标签')

    # 统计
    usage_count = db.Column(db.Integer, default=0, comment='使用次数')
    tools_count = db.Column(db.Integer, default=0, comment='MCP提供的工具数量')
    resources_count = db.Column(db.Integer, default=0, comment='MCP提供的资源数量')
    last_sync_at = db.Column(db.DateTime, comment='最后同步时间')
    last_used_at = db.Column(db.DateTime, comment='最后使用时间')

    # 软删除
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.String(100), comment='创建人')
    updated_by = db.Column(db.String(100), comment='更新人')

    # 关系
    tenant = db.relationship('Tenant', backref='mcp_servers')
    skills = db.relationship('Skill', backref='mcp_server', lazy='dynamic',
                            cascade='all, delete-orphan')
    tools = db.relationship('MCPTool', backref='mcp_server', lazy='dynamic',
                           cascade='all, delete-orphan')
    resources = db.relationship('MCPResource', backref='mcp_server', lazy='dynamic',
                               cascade='all, delete-orphan')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'code': self.code,
            'transport_type': self.transport_type,
            'command': self.command,
            'arguments': self.arguments,
            'env': self.env,
            'url': self.url,
            'timeout': self.timeout,
            'status': self.status,
            'is_enabled': self.is_enabled,
            'is_builtin': self.is_builtin,
            'tags': self.tags,
            'usage_count': self.usage_count,
            'tools_count': self.tools_count,
            'resources_count': self.resources_count,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'skills_count': self.skills.count()
        }


class MCPTool(db.Model):
    """MCP工具模型"""
    __tablename__ = 'mcp_tools'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    mcp_id = db.Column(db.Integer, db.ForeignKey('mcp_servers.id'), nullable=False, index=True, comment='MCP服务器ID')

    # 工具信息
    name = db.Column(db.String(200), nullable=False, comment='工具名称')
    description = db.Column(db.Text, comment='工具描述')
    input_schema = db.Column(db.Text, comment='JSON格式的输入schema')

    # 统计
    usage_count = db.Column(db.Integer, default=0, comment='使用次数')
    last_used_at = db.Column(db.DateTime, comment='最后使用时间')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    executions = db.relationship('MCPToolExecution', backref='tool', lazy='dynamic',
                                cascade='all, delete-orphan')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'mcp_id': self.mcp_id,
            'name': self.name,
            'description': self.description,
            'input_schema': self.input_schema,
            'usage_count': self.usage_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MCPResource(db.Model):
    """MCP资源模型"""
    __tablename__ = 'mcp_resources'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    mcp_id = db.Column(db.Integer, db.ForeignKey('mcp_servers.id'), nullable=False, index=True, comment='MCP服务器ID')

    # 资源信息
    uri = db.Column(db.String(500), nullable=False, comment='资源URI')
    name = db.Column(db.String(200), comment='资源名称')
    description = db.Column(db.Text, comment='资源描述')
    mime_type = db.Column(db.String(100), comment='MIME类型')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'mcp_id': self.mcp_id,
            'uri': self.uri,
            'name': self.name,
            'description': self.description,
            'mime_type': self.mime_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MCPToolExecution(db.Model):
    """MCP工具执行记录"""
    __tablename__ = 'mcp_tool_executions'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    tool_id = db.Column(db.Integer, db.ForeignKey('mcp_tools.id'), nullable=False, index=True, comment='工具ID')

    # 执行信息
    parameters = db.Column(db.Text, comment='JSON格式的参数')
    result = db.Column(db.Text, comment='JSON格式的结果')
    status = db.Column(db.String(20), default='success', comment='状态: success, error')
    error_message = db.Column(db.Text, comment='错误消息')
    execution_time = db.Column(db.Float, comment='执行时间（秒）')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tool_id': self.tool_id,
            'parameters': self.parameters,
            'result': self.result,
            'status': self.status,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
