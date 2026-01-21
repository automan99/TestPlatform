"""
LLM模型配置管理API
支持常见大语言模型配置管理
"""
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import LLMModel
from app.utils import success_response, error_response
from app.utils.crypto import encrypt_data, decrypt_data
import requests
from datetime import datetime

# 命名空间
llm_model_ns = Namespace('LLMModels', description='LLM模型配置管理')

# Swagger模型定义
llm_model_model = llm_model_ns.model('LLMModel', {
    'name': fields.String(required=True, description='模型名称'),
    'provider': fields.String(required=True, description='提供商: openai, anthropic, azure, etc.'),
    'model_id': fields.String(required=True, description='模型ID: gpt-4, claude-3-opus-20240229, etc.'),
    'api_key': fields.String(description='API密钥'),
    'api_base': fields.String(description='API基础URL'),
    'api_version': fields.String(description='API版本(用于Azure等)'),
    'temperature': fields.Float(description='温度参数'),
    'max_tokens': fields.Integer(description='最大token数'),
    'top_p': fields.Float(description='top_p参数'),
    'frequency_penalty': fields.Float(description='频率惩罚'),
    'presence_penalty': fields.Float(description='存在惩罚'),
    'is_default': fields.Boolean(description='是否为默认模型'),
    'is_enabled': fields.Boolean(description='是否启用'),
    'description': fields.String(description='描述')
})


# ============== LLM模型列表API ==============
@llm_model_ns.route('')
class LLMModelListAPI(Resource):
    """LLM模型列表API"""

    @llm_model_ns.doc('get_llm_models')
    def get(self):
        """获取LLM模型列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            provider = request.args.get('provider')
            keyword = request.args.get('keyword')
            is_enabled = request.args.get('is_enabled')

            query = LLMModel.query

            if provider:
                query = query.filter_by(provider=provider)
            if is_enabled is not None:
                is_enabled_bool = is_enabled.lower() == 'true'
                query = query.filter_by(is_enabled=is_enabled_bool)
            if keyword:
                query = query.filter(
                    db.or_(
                        LLMModel.name.like(f'%{keyword}%'),
                        LLMModel.model_id.like(f'%{keyword}%')
                    )
                )

            pagination = query.order_by(LLMModel.is_default.desc(), LLMModel.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            # 脱敏API密钥
            items = []
            for model in pagination.items:
                model_dict = model.to_dict()
                if model_dict.get('api_key'):
                    # 只显示前8位和后4位
                    api_key = model_dict['api_key']
                    if len(api_key) > 12:
                        model_dict['api_key'] = api_key[:8] + '****' + api_key[-4:]
                    else:
                        model_dict['api_key'] = '****'
                items.append(model_dict)

            return success_response(data={
                'items': items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            })
        except Exception as e:
            current_app.logger.error(f'获取LLM模型列表失败: {str(e)}')
            return error_response(message=f'获取LLM模型列表失败: {str(e)}', code=500)

    @llm_model_ns.doc('create_llm_model')
    @llm_model_ns.expect(llm_model_model)
    def post(self):
        """创建LLM模型配置"""
        try:
            data = request.get_json()

            # 验证必填字段
            required_fields = ['name', 'provider', 'model_id', 'api_key']
            for field in required_fields:
                if field not in data:
                    return error_response(message=f'缺少必填字段: {field}', code=400)

            # 检查模型名称是否重复
            if LLMModel.query.filter_by(name=data['name']).first():
                return error_response(message='模型名称已存在', code=400)

            # 如果设置为默认，取消其他模型的默认状态
            if data.get('is_default'):
                LLMModel.query.filter_by(is_default=True).update({'is_default': False})

            # 加密API密钥
            encrypted_key = encrypt_data(data['api_key'])

            # 创建模型配置
            model = LLMModel(
                name=data['name'],
                provider=data['provider'],
                model_id=data['model_id'],
                api_key=encrypted_key,
                api_base=data.get('api_base'),
                api_version=data.get('api_version'),
                temperature=data.get('temperature', 0.7),
                max_tokens=data.get('max_tokens', 4096),
                top_p=data.get('top_p', 1.0),
                frequency_penalty=data.get('frequency_penalty', 0.0),
                presence_penalty=data.get('presence_penalty', 0.0),
                is_default=data.get('is_default', False),
                is_enabled=data.get('is_enabled', True),
                description=data.get('description')
            )

            db.session.add(model)
            db.session.commit()

            return success_response(data=model.to_dict(), message='创建成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建LLM模型失败: {str(e)}')
            return error_response(message=f'创建LLM模型失败: {str(e)}', code=500)


# ============== LLM模型详情API ==============
@llm_model_ns.route('/<int:model_id>')
class LLMModelAPI(Resource):
    """LLM模型详情API"""

    @llm_model_ns.doc('get_llm_model')
    def get(self, model_id):
        """获取LLM模型详情"""
        try:
            model = LLMModel.query.get(model_id)
            if not model:
                return error_response(message='模型不存在', code=404)

            model_dict = model.to_dict()
            # 脱敏API密钥
            if model_dict.get('api_key'):
                api_key = model_dict['api_key']
                if len(api_key) > 12:
                    model_dict['api_key'] = api_key[:8] + '****' + api_key[-4:]
                else:
                    model_dict['api_key'] = '****'

            return success_response(data=model_dict)
        except Exception as e:
            current_app.logger.error(f'获取LLM模型详情失败: {str(e)}')
            return error_response(message=f'获取LLM模型详情失败: {str(e)}', code=500)

    @llm_model_ns.doc('update_llm_model')
    @llm_model_ns.expect(llm_model_model)
    def put(self, model_id):
        """更新LLM模型配置"""
        try:
            model = LLMModel.query.get(model_id)
            if not model:
                return error_response(message='模型不存在', code=404)

            data = request.get_json()

            # 检查模型名称是否重复
            if 'name' in data and data['name'] != model.name:
                if LLMModel.query.filter_by(name=data['name']).first():
                    return error_response(message='模型名称已存在', code=400)

            # 如果设置为默认，取消其他模型的默认状态
            if data.get('is_default'):
                LLMModel.query.filter(LLMModel.id != model_id, LLMModel.is_default == True).update({'is_default': False})

            # 更新字段
            if 'name' in data:
                model.name = data['name']
            if 'provider' in data:
                model.provider = data['provider']
            if 'model_id' in data:
                model.model_id = data['model_id']
            if 'api_key' in data:
                model.api_key = encrypt_data(data['api_key'])
            if 'api_base' in data:
                model.api_base = data['api_base']
            if 'api_version' in data:
                model.api_version = data['api_version']
            if 'temperature' in data:
                model.temperature = data['temperature']
            if 'max_tokens' in data:
                model.max_tokens = data['max_tokens']
            if 'top_p' in data:
                model.top_p = data['top_p']
            if 'frequency_penalty' in data:
                model.frequency_penalty = data['frequency_penalty']
            if 'presence_penalty' in data:
                model.presence_penalty = data['presence_penalty']
            if 'is_default' in data:
                model.is_default = data['is_default']
            if 'is_enabled' in data:
                model.is_enabled = data['is_enabled']
            if 'description' in data:
                model.description = data['description']

            model.updated_at = datetime.utcnow()
            db.session.commit()

            return success_response(data=model.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'更新LLM模型失败: {str(e)}')
            return error_response(message=f'更新LLM模型失败: {str(e)}', code=500)

    @llm_model_ns.doc('delete_llm_model')
    def delete(self, model_id):
        """删除LLM模型配置"""
        try:
            model = LLMModel.query.get(model_id)
            if not model:
                return error_response(message='模型不存在', code=404)

            db.session.delete(model)
            db.session.commit()

            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'删除LLM模型失败: {str(e)}')
            return error_response(message=f'删除LLM模型失败: {str(e)}', code=500)


# ============== 测试LLM模型连接 ==============
@llm_model_ns.route('/<int:model_id>/test')
class LLMModelTestAPI(Resource):
    """测试LLM模型连接API"""

    @llm_model_ns.doc('test_llm_model')
    def post(self, model_id):
        """测试LLM模型连接"""
        try:
            model = LLMModel.query.get(model_id)
            if not model:
                return error_response(message='模型不存在', code=404)

            # 解密API密钥
            api_key = decrypt_data(model.api_key)

            # 根据提供商构建测试请求
            headers = {
                'Content-Type': 'application/json'
            }

            if model.provider == 'openai':
                headers['Authorization'] = f'Bearer {api_key}'
                api_base = model.api_base or 'https://api.openai.com/v1'
                endpoint = f'{api_base.rstrip("/")}/models'
            elif model.provider == 'anthropic':
                headers['x-api-key'] = api_key
                headers['anthropic-version'] = '2023-06-01'
                api_base = model.api_base or 'https://api.anthropic.com'
                endpoint = f'{api_base.rstrip("/")}/v1/messages'
            elif model.provider == 'azure':
                headers['api-key'] = api_key
                api_base = model.api_base
                endpoint = f'{api_base.rstrip("/")}/openai/deployments?api-version={model.api_version or "2024-02-15-preview"}'
            else:
                return error_response(message=f'不支持的提供商: {model.provider}', code=400)

            # 发送测试请求
            try:
                if model.provider == 'anthropic':
                    # Anthropic发送一个简单的消息请求
                    test_data = {
                        'model': model.model_id,
                        'max_tokens': 10,
                        'messages': [{'role': 'user', 'content': 'Hi'}]
                    }
                    response = requests.post(endpoint, headers=headers, json=test_data, timeout=10)
                else:
                    response = requests.get(endpoint, headers=headers, timeout=10)

                if response.status_code in [200, 201]:
                    return success_response(message='连接成功', data={'status': 'success'})
                else:
                    return error_response(
                        message=f'连接失败: {response.status_code} {response.text[:200]}',
                        code=400
                    )
            except requests.Timeout:
                return error_response(message='连接超时，请检查网络或API地址', code=400)
            except requests.RequestException as e:
                return error_response(message=f'连接失败: {str(e)}', code=400)

        except Exception as e:
            current_app.logger.error(f'测试LLM模型失败: {str(e)}')
            return error_response(message=f'测试LLM模型失败: {str(e)}', code=500)


# ============== 获取提供商列表 ==============
@llm_model_ns.route('/providers')
class LLMModelProvidersAPI(Resource):
    """LLM模型提供商API"""

    @llm_model_ns.doc('get_providers')
    def get(self):
        """获取支持的提供商列表"""
        try:
            providers = [
                {
                    'value': 'openai',
                    'label': 'OpenAI',
                    'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-4o', 'gpt-4o-mini'],
                    'api_base': 'https://api.openai.com/v1',
                    'auth_type': 'bearer_token'
                },
                {
                    'value': 'anthropic',
                    'label': 'Anthropic',
                    'models': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307', 'claude-3-5-sonnet-20240620'],
                    'api_base': 'https://api.anthropic.com',
                    'auth_type': 'api_key'
                },
                {
                    'value': 'azure',
                    'label': 'Azure OpenAI',
                    'models': ['gpt-4', 'gpt-35-turbo'],
                    'api_base': '',
                    'auth_type': 'api_key'
                },
                {
                    'value': 'deepseek',
                    'label': 'DeepSeek',
                    'models': ['deepseek-chat', 'deepseek-coder'],
                    'api_base': 'https://api.deepseek.com/v1',
                    'auth_type': 'bearer_token'
                },
                {
                    'value': 'moonshot',
                    'label': 'Moonshot AI',
                    'models': ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
                    'api_base': 'https://api.moonshot.cn/v1',
                    'auth_type': 'bearer_token'
                },
                {
                    'value': 'zhipu',
                    'label': '智谱AI',
                    'models': ['glm-4', 'glm-3-turbo'],
                    'api_base': 'https://open.bigmodel.cn/api/paas/v4',
                    'auth_type': 'bearer_token'
                },
                {
                    'value': 'baichuan',
                    'label': '百川智能',
                    'models': ['Baichuan2-Turbo', 'Baichuan2-53B'],
                    'api_base': 'https://api.baichuan-ai.com/v1',
                    'auth_type': 'bearer_token'
                }
            ]
            return success_response(data=providers)
        except Exception as e:
            current_app.logger.error(f'获取提供商列表失败: {str(e)}')
            return error_response(message=f'获取提供商列表失败: {str(e)}', code=500)
