"""
Git技能仓库管理API
"""
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import SkillRepository, GitCredential, GitSkill, SkillSyncLog
from app.utils import success_response, error_response, encrypt_data
from app.services.git_sync_service import get_git_sync_service
import json
from datetime import datetime
import traceback

# 命名空间
skill_repository_ns = Namespace('SkillRepositories', description='技能仓库管理')
git_skill_ns = Namespace('GitSkills', description='Git技能管理')

# Swagger模型定义
git_credential_model = skill_repository_ns.model('GitCredential', {
    'name': fields.String(required=True, description='凭证名称'),
    'description': fields.String(description='凭证描述'),
    'auth_type': fields.String(required=True, description='认证类型: token, ssh_key'),
    'github_token': fields.String(description='GitHub Personal Access Token'),
    'ssh_key_content': fields.String(description='SSH私钥内容'),
    'ssh_key_passphrase': fields.String(description='SSH密钥密码'),
    'github_login': fields.String(description='GitHub用户名')
})

skill_repository_model = skill_repository_ns.model('SkillRepository', {
    'name': fields.String(required=True, description='仓库名称'),
    'description': fields.String(description='仓库描述'),
    'git_url': fields.String(required=True, description='Git仓库URL'),
    'branch': fields.String(description='分支名称'),
    'skills_path': fields.String(description='技能文件路径'),
    'auth_type': fields.String(description='认证类型: public, token, ssh_key'),
    'git_credential_id': fields.Integer(description='Git凭证ID'),
    'sync_mode': fields.String(description='同步模式: manual, scheduled, webhook'),
    'sync_interval': fields.Integer(description='定时同步间隔(分钟)'),
    'webhook_secret': fields.String(description='Webhook密钥'),
    'is_enabled': fields.Boolean(description='是否启用'),
    'auto_sync': fields.Boolean(description='是否自动同步')
})

git_skill_model = git_skill_ns.model('GitSkill', {
    'name': fields.String(description='技能名称'),
    'code': fields.String(description='技能代码'),
    'description': fields.String(description='技能描述'),
    'script_content': fields.String(description='技能内容'),
    'script_type': fields.String(description='脚本类型'),
    'params_schema': fields.String(description='参数定义'),
    'status': fields.String(description='状态'),
    'is_enabled': fields.Boolean(description='是否启用')
})


# ============== GitCredential API ==============

@skill_repository_ns.route('/credentials')
class GitCredentialListAPI(Resource):
    """Git凭证列表API"""

    def get(self):
        """获取Git凭证列表"""
        try:
            credentials = GitCredential.query.all()
            return success_response(data={
                'items': [cred.to_dict() for cred in credentials],
                'total': len(credentials)
            })
        except Exception as e:
            current_app.logger.error(f'获取Git凭证列表失败: {str(e)}')
            return error_response(message=f'获取Git凭证列表失败: {str(e)}', code=500)

    @skill_repository_ns.expect(git_credential_model)
    def post(self):
        """创建Git凭证"""
        try:
            data = request.get_json()

            credential = GitCredential(
                name=data.get('name'),
                description=data.get('description'),
                auth_type=data.get('auth_type'),
                github_login=data.get('github_login'),
                created_by=data.get('created_by')
            )

            # 加密存储敏感信息
            if data.get('auth_type') == 'token' and data.get('github_token'):
                credential.github_token = encrypt_data(data['github_token'])

            if data.get('auth_type') == 'ssh_key':
                if data.get('ssh_key_content'):
                    credential.ssh_key_content = encrypt_data(data['ssh_key_content'])
                if data.get('ssh_key_passphrase'):
                    credential.ssh_key_passphrase = encrypt_data(data['ssh_key_passphrase'])

            db.session.add(credential)
            db.session.commit()

            return success_response(data=credential.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建Git凭证失败: {str(e)}')
            return error_response(message=f'创建Git凭证失败: {str(e)}', code=500)


@skill_repository_ns.route('/credentials/<int:credential_id>')
class GitCredentialAPI(Resource):
    """Git凭证详情API"""

    def get(self, credential_id):
        """获取Git凭证详情"""
        try:
            credential = GitCredential.query.get(credential_id)
            if not credential:
                return error_response(message='凭证不存在', code=404)
            return success_response(data=credential.to_dict())
        except Exception as e:
            return error_response(message=f'获取Git凭证失败: {str(e)}', code=500)

    @skill_repository_ns.expect(git_credential_model)
    def put(self, credential_id):
        """更新Git凭证"""
        try:
            credential = GitCredential.query.get(credential_id)
            if not credential:
                return error_response(message='凭证不存在', code=404)

            data = request.get_json()

            credential.name = data.get('name', credential.name)
            credential.description = data.get('description', credential.description)
            credential.auth_type = data.get('auth_type', credential.auth_type)
            credential.github_login = data.get('github_login', credential.github_login)

            # 加密存储敏感信息
            if data.get('github_token'):
                credential.github_token = encrypt_data(data['github_token'])
            if data.get('ssh_key_content'):
                credential.ssh_key_content = encrypt_data(data['ssh_key_content'])
            if data.get('ssh_key_passphrase'):
                credential.ssh_key_passphrase = encrypt_data(data['ssh_key_passphrase'])

            db.session.commit()
            return success_response(data=credential.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'更新Git凭证失败: {str(e)}')
            return error_response(message=f'更新Git凭证失败: {str(e)}', code=500)

    def delete(self, credential_id):
        """删除Git凭证"""
        try:
            credential = GitCredential.query.get(credential_id)
            if not credential:
                return error_response(message='凭证不存在', code=404)

            # 检查是否有仓库使用此凭证
            if credential.repositories.count() > 0:
                return error_response(message='该凭证正在被使用，无法删除', code=400)

            db.session.delete(credential)
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'删除Git凭证失败: {str(e)}')
            return error_response(message=f'删除Git凭证失败: {str(e)}', code=500)


# ============== SkillRepository API ==============

@skill_repository_ns.route('')
class SkillRepositoryListAPI(Resource):
    """技能仓库列表API"""

    def get(self):
        """获取技能仓库列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            keyword = request.args.get('keyword')
            auth_type = request.args.get('auth_type')
            sync_mode = request.args.get('sync_mode')
            status = request.args.get('status')
            is_enabled = request.args.get('is_enabled')

            query = SkillRepository.query

            if keyword:
                query = query.filter(SkillRepository.name.contains(keyword))
            if auth_type:
                query = query.filter_by(auth_type=auth_type)
            if sync_mode:
                query = query.filter_by(sync_mode=sync_mode)
            if status:
                query = query.filter_by(status=status)
            if is_enabled is not None:
                is_enabled_bool = is_enabled.lower() == 'true'
                query = query.filter_by(is_enabled=is_enabled_bool)

            pagination = query.order_by(SkillRepository.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(data={
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取技能仓库列表失败: {str(e)}')
            return error_response(message=f'获取技能仓库列表失败: {str(e)}', code=500)

    @skill_repository_ns.expect(skill_repository_model)
    def post(self):
        """创建技能仓库"""
        try:
            data = request.get_json()

            repository = SkillRepository(
                name=data.get('name'),
                description=data.get('description'),
                git_url=data.get('git_url'),
                branch=data.get('branch', 'main'),
                skills_path=data.get('skills_path', '/'),
                auth_type=data.get('auth_type', 'public'),
                git_credential_id=data.get('git_credential_id'),
                sync_mode=data.get('sync_mode', 'manual'),
                sync_interval=data.get('sync_interval', 60),
                webhook_secret=data.get('webhook_secret'),
                is_enabled=data.get('is_enabled', True),
                auto_sync=data.get('auto_sync', False),
                created_by=data.get('created_by')
            )

            db.session.add(repository)
            db.session.commit()

            return success_response(data=repository.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建技能仓库失败: {str(e)}')
            return error_response(message=f'创建技能仓库失败: {str(e)}', code=500)


@skill_repository_ns.route('/<int:repo_id>')
class SkillRepositoryAPI(Resource):
    """技能仓库详情API"""

    def get(self, repo_id):
        """获取技能仓库详情"""
        try:
            repository = SkillRepository.query.get(repo_id)
            if not repository:
                return error_response(message='仓库不存在', code=404)
            return success_response(data=repository.to_dict())
        except Exception as e:
            return error_response(message=f'获取技能仓库失败: {str(e)}', code=500)

    @skill_repository_ns.expect(skill_repository_model)
    def put(self, repo_id):
        """更新技能仓库"""
        try:
            repository = SkillRepository.query.get(repo_id)
            if not repository:
                return error_response(message='仓库不存在', code=404)

            data = request.get_json()

            repository.name = data.get('name', repository.name)
            repository.description = data.get('description', repository.description)
            repository.git_url = data.get('git_url', repository.git_url)
            repository.branch = data.get('branch', repository.branch)
            repository.skills_path = data.get('skills_path', repository.skills_path)
            repository.auth_type = data.get('auth_type', repository.auth_type)
            repository.git_credential_id = data.get('git_credential_id', repository.git_credential_id)
            repository.sync_mode = data.get('sync_mode', repository.sync_mode)
            repository.sync_interval = data.get('sync_interval', repository.sync_interval)
            repository.webhook_secret = data.get('webhook_secret', repository.webhook_secret)
            repository.is_enabled = data.get('is_enabled', repository.is_enabled)
            repository.auto_sync = data.get('auto_sync', repository.auto_sync)

            db.session.commit()
            return success_response(data=repository.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'更新技能仓库失败: {str(e)}')
            return error_response(message=f'更新技能仓库失败: {str(e)}', code=500)

    def delete(self, repo_id):
        """删除技能仓库"""
        try:
            repository = SkillRepository.query.get(repo_id)
            if not repository:
                return error_response(message='仓库不存在', code=404)

            # 先删除关联的Git技能记录
            GitSkill.query.filter_by(repository_id=repo_id).delete()

            # 先删除关联的同步日志记录
            SkillSyncLog.query.filter_by(repository_id=repo_id).delete()

            # 删除仓库文件
            sync_service = get_git_sync_service()
            sync_service.delete_repo_files(repo_id)

            # 最后删除仓库记录
            db.session.delete(repository)
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'删除技能仓库失败: {str(e)}')
            return error_response(message=f'删除技能仓库失败: {str(e)}', code=500)


@skill_repository_ns.route('/<int:repo_id>/sync')
class SkillRepositorySyncAPI(Resource):
    """同步技能仓库API"""

    def post(self, repo_id):
        """手动同步技能仓库"""
        try:
            repository = SkillRepository.query.get(repo_id)
            if not repository:
                return error_response(message='仓库不存在', code=404)

            if not repository.is_enabled:
                return error_response(message='仓库已禁用', code=400)

            sync_service = get_git_sync_service()
            result = sync_service.sync(repo_id, sync_type='manual', triggered_by=request.args.get('user', 'system'))

            if result['success']:
                return success_response(data=result, message='同步成功')
            else:
                return error_response(message=result.get('error', '同步失败'), code=500)
        except Exception as e:
            current_app.logger.error(f'同步技能仓库失败: {str(e)}\n{traceback.format_exc()}')
            return error_response(message=f'同步失败: {str(e)}', code=500)


@skill_repository_ns.route('/<int:repo_id>/sync-logs')
class SkillRepositorySyncLogsAPI(Resource):
    """技能仓库同步日志API"""

    def get(self, repo_id):
        """获取同步日志"""
        try:
            repository = SkillRepository.query.get(repo_id)
            if not repository:
                return error_response(message='仓库不存在', code=404)

            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)

            pagination = SkillSyncLog.query.filter_by(
                repository_id=repo_id
            ).order_by(
                SkillSyncLog.started_at.desc()
            ).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(data={
                'items': [log.to_dict() for log in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取同步日志失败: {str(e)}')
            return error_response(message=f'获取同步日志失败: {str(e)}', code=500)


@skill_repository_ns.route('/webhook/<int:repo_id>')
class SkillRepositoryWebhookAPI(Resource):
    """技能仓库Webhook API"""

    def post(self, repo_id):
        """处理GitHub Webhook推送"""
        try:
            repository = SkillRepository.query.get(repo_id)
            if not repository:
                return error_response(message='仓库不存在', code=404)

            if not repository.is_enabled:
                return error_response(message='仓库已禁用', code=400)

            if repository.sync_mode != 'webhook':
                return error_response(message='仓库未启用webhook同步', code=400)

            # 验证webhook secret
            webhook_secret = request.headers.get('X-Hub-Signature-256')
            if repository.webhook_secret and webhook_secret:
                # 这里可以添加HMAC验证
                pass

            # 获取GitHub webhook payload
            data = request.get_json()
            if not data:
                return error_response(message='无效的webhook payload', code=400)

            # 检查是否是push事件
            if data.get('ref') and repository.branch in data.get('ref', ''):
                sync_service = get_git_sync_service()
                result = sync_service.sync(repo_id, sync_type='webhook', triggered_by='webhook')

                if result['success']:
                    return success_response(data=result, message='Webhook触发同步成功')
                else:
                    return error_response(message=result.get('error', '同步失败'), code=500)

            return success_response(message='Webhook接收成功，无需同步')
        except Exception as e:
            current_app.logger.error(f'处理webhook失败: {str(e)}\n{traceback.format_exc()}')
            return error_response(message=f'Webhook处理失败: {str(e)}', code=500)


# ============== GitSkill API ==============

@git_skill_ns.route('')
class GitSkillListAPI(Resource):
    """Git技能列表API"""

    def get(self):
        """获取Git技能列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            keyword = request.args.get('keyword')
            repository_id = request.args.get('repository_id', type=int)
            script_type = request.args.get('script_type')
            status = request.args.get('status')
            is_enabled = request.args.get('is_enabled')

            query = GitSkill.query

            if keyword:
                query = query.filter(
                    GitSkill.name.contains(keyword) |
                    GitSkill.code.contains(keyword) |
                    GitSkill.description.contains(keyword)
                )
            if repository_id:
                query = query.filter_by(repository_id=repository_id)
            if script_type:
                query = query.filter_by(script_type=script_type)
            if status:
                query = query.filter_by(status=status)
            if is_enabled is not None:
                is_enabled_bool = is_enabled.lower() == 'true'
                query = query.filter_by(is_enabled=is_enabled_bool)

            pagination = query.order_by(GitSkill.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(data={
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取Git技能列表失败: {str(e)}')
            return error_response(message=f'获取Git技能列表失败: {str(e)}', code=500)


@git_skill_ns.route('/<int:skill_id>')
class GitSkillAPI(Resource):
    """Git技能详情API"""

    def get(self, skill_id):
        """获取Git技能详情"""
        try:
            skill = GitSkill.query.get(skill_id)
            if not skill:
                return error_response(message='技能不存在', code=404)
            return success_response(data=skill.to_dict())
        except Exception as e:
            return error_response(message=f'获取Git技能失败: {str(e)}', code=500)

    @git_skill_ns.expect(git_skill_model)
    def put(self, skill_id):
        """更新Git技能（只允许更新状态和启用设置）"""
        try:
            skill = GitSkill.query.get(skill_id)
            if not skill:
                return error_response(message='技能不存在', code=404)

            data = request.get_json()

            # Git技能只允许更新状态相关字段，其他字段从Git同步
            skill.status = data.get('status', skill.status)
            skill.is_enabled = data.get('is_enabled', skill.is_enabled)

            db.session.commit()
            return success_response(data=skill.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'更新Git技能失败: {str(e)}')
            return error_response(message=f'更新Git技能失败: {str(e)}', code=500)


@git_skill_ns.route('/<int:skill_id>/execute')
class GitSkillExecuteAPI(Resource):
    """执行Git技能API"""

    def post(self, skill_id):
        """执行Git技能"""
        try:
            skill = GitSkill.query.get(skill_id)
            if not skill:
                return error_response(message='技能不存在', code=404)

            if not skill.is_enabled:
                return error_response(message='技能已禁用', code=400)

            data = request.get_json()
            params = data.get('params', {})

            # TODO: 实现具体的技能执行逻辑
            result = {
                'success': True,
                'message': '执行成功',
                'output': f'技能 {skill.name} 执行完成',
                'params': params
            }

            # 更新统计
            skill.usage_count += 1
            skill.last_used_at = datetime.utcnow()
            db.session.commit()

            return success_response(data=result, message='执行成功')
        except Exception as e:
            current_app.logger.error(f'执行Git技能失败: {str(e)}')
            return error_response(message=f'执行Git技能失败: {str(e)}', code=500)
