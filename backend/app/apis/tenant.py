"""
租户管理API
"""
from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import Tenant, TenantUser, User
from app.utils import success_response, error_response
from app.utils.permissions import (
    require_super_admin,
    require_tenant_admin,
    require_tenant_member,
    can_manage_tenant,
    check_tenant_user_limit,
    get_current_user
)
from datetime import datetime, date

# 命名空间
tenant_ns = Namespace('Tenants', description='租户管理')

# Swagger模型定义
tenant_model = tenant_ns.model('Tenant', {
    'name': fields.String(required=True, description='租户名称'),
    'code': fields.String(required=True, description='租户代码'),
    'description': fields.String(description='描述'),
    'logo': fields.String(description='Logo URL'),
    'status': fields.String(description='状态'),
    'max_users': fields.Integer(description='最大用户数'),
    'max_projects': fields.Integer(description='最大项目数'),
    'max_storage_gb': fields.Integer(description='最大存储空间(GB)'),
    'expire_date': fields.String(description='过期日期(YYYY-MM-DD)'),
    'settings': fields.Raw(description='租户设置(JSON)')
})

add_member_model = tenant_ns.model('AddMember', {
    'user_id': fields.Integer(required=True, description='用户ID'),
    'role': fields.String(description='角色: owner-所有者, admin-管理员, member-成员', default='member')
})

update_member_role_model = tenant_ns.model('UpdateMemberRole', {
    'role': fields.String(required=True, description='角色: owner-所有者, admin-管理员, member-成员')
})


# ============== 租户管理API ==============

@tenant_ns.route('')
class TenantListAPI(Resource):
    """租户列表API"""

    def get(self):
        """获取租户列表"""
        try:
            current_user = get_current_user()
            if not current_user:
                return error_response(message='未登录或登录已过期', code=401)

            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            status = request.args.get('status')
            keyword = request.args.get('keyword')

            query = Tenant.query.filter_by(is_deleted=False)

            # 超级管理员可以查看所有租户
            # 普通用户只能查看自己所属的租户
            if not current_user.is_super_admin():
                tenant_ids = [tu.tenant_id for tu in current_user.tenant_users.filter_by(is_deleted=False).all()]
                if not tenant_ids:
                    return success_response(data={'items': [], 'total': 0, 'pages': 0, 'current_page': page})
                query = query.filter(Tenant.id.in_(tenant_ids))

            if status:
                query = query.filter_by(status=status)
            if keyword:
                query = query.filter(Tenant.name.contains(keyword) |
                                     Tenant.code.contains(keyword))

            pagination = query.order_by(Tenant.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            items = []
            for item in pagination.items:
                item_dict = item.to_dict()
                # 添加当前用户在该租户中的角色
                if current_user.is_super_admin():
                    item_dict['user_role'] = 'super_admin'
                    item_dict['user_role_name'] = '超级管理员'
                else:
                    tenant_user = TenantUser.query.filter_by(
                        tenant_id=item.id,
                        user_id=current_user.id,
                        is_deleted=False
                    ).first()
                    if tenant_user:
                        item_dict['user_role'] = tenant_user.role
                        role_names = {'owner': '所有者', 'admin': '管理员', 'member': '成员'}
                        item_dict['user_role_name'] = role_names.get(tenant_user.role, tenant_user.role)
                items.append(item_dict)

            return success_response(data={
                'items': items,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取租户列表失败: {str(e)}')
            return error_response(message=f'获取租户列表失败: {str(e)}', code=500)

    @tenant_ns.expect(tenant_model)
    @require_super_admin
    def post(self):
        """创建租户（仅超级管理员）"""
        try:
            data = request.get_json()

            # 检查租户代码是否已存在
            if Tenant.query.filter_by(code=data['code']).first():
                return error_response(message='租户代码已存在', code=400)

            # 检查租户名称是否已存在
            if Tenant.query.filter_by(name=data['name']).first():
                return error_response(message='租户名称已存在', code=400)

            # 处理过期日期
            expire_date = None
            if data.get('expire_date'):
                expire_date = datetime.strptime(data.get('expire_date'), '%Y-%m-%d').date()

            tenant = Tenant(
                name=data.get('name'),
                code=data.get('code'),
                description=data.get('description'),
                logo=data.get('logo'),
                status=data.get('status', 'active'),
                max_users=data.get('max_users', 10),
                max_projects=data.get('max_projects', 5),
                max_storage_gb=data.get('max_storage_gb', 10),
                expire_date=expire_date,
                settings=data.get('settings'),
                created_by=g.current_user.id
            )

            db.session.add(tenant)
            db.session.commit()

            return success_response(data=tenant.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建租户失败: {str(e)}')
            return error_response(message=f'创建租户失败: {str(e)}', code=500)


@tenant_ns.route('/<int:tenant_id>')
class TenantAPI(Resource):
    """租户详情API"""

    @require_tenant_member
    def get(self, tenant_id):
        """获取租户详情"""
        try:
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()
            tenant_dict = tenant.to_dict()

            # 添加当前用户在该租户中的角色
            if g.is_super_admin:
                tenant_dict['current_user_role'] = 'super_admin'
            else:
                tenant_dict['current_user_role'] = g.current_tenant_role

            return success_response(data=tenant_dict)
        except Exception as e:
            return error_response(message=f'获取租户详情失败: {str(e)}', code=500)

    @tenant_ns.expect(tenant_model)
    @require_super_admin
    def put(self, tenant_id):
        """更新租户（仅超级管理员）"""
        try:
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()
            data = request.get_json()

            # 检查租户代码是否被其他租户使用
            if data.get('code') and data['code'] != tenant.code:
                if Tenant.query.filter_by(code=data['code']).first():
                    return error_response(message='租户代码已存在', code=400)

            # 检查租户名称是否被其他租户使用
            if data.get('name') and data['name'] != tenant.name:
                if Tenant.query.filter_by(name=data['name']).first():
                    return error_response(message='租户名称已存在', code=400)

            tenant.name = data.get('name', tenant.name)
            tenant.code = data.get('code', tenant.code)
            tenant.description = data.get('description', tenant.description)
            tenant.logo = data.get('logo', tenant.logo)
            tenant.status = data.get('status', tenant.status)
            tenant.max_users = data.get('max_users', tenant.max_users)
            tenant.max_projects = data.get('max_projects', tenant.max_projects)
            tenant.max_storage_gb = data.get('max_storage_gb', tenant.max_storage_gb)

            if data.get('expire_date'):
                tenant.expire_date = datetime.strptime(data.get('expire_date'), '%Y-%m-%d').date()

            if data.get('settings') is not None:
                tenant.settings = data.get('settings')

            tenant.updated_by = g.current_user.id

            db.session.commit()
            return success_response(data=tenant.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新租户失败: {str(e)}', code=500)

    @require_super_admin
    def delete(self, tenant_id):
        """删除租户（仅超级管理员，软删除）"""
        try:
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()

            # 检查是否有关联数据
            tenant_user_count = TenantUser.query.filter_by(
                tenant_id=tenant_id,
                is_deleted=False
            ).count()
            if tenant_user_count > 0:
                return error_response(message='该租户下有用户，无法删除', code=400)

            tenant.is_deleted = True
            tenant.updated_by = g.current_user.id
            db.session.commit()

            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除租户失败: {str(e)}', code=500)


@tenant_ns.route('/<int:tenant_id>/users')
class TenantUsersAPI(Resource):
    """租户用户列表API"""

    @require_tenant_member
    def get(self, tenant_id):
        """获取租户用户列表"""
        try:
            # 验证租户存在
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()

            tenant_users = TenantUser.query.filter_by(
                tenant_id=tenant_id,
                is_deleted=False
            ).all()

            users_data = []
            for tu in tenant_users:
                user = User.query.get(tu.user_id)
                if user:
                    user_dict = user.to_dict()
                    user_dict['tenant_role'] = tu.role
                    user_dict['tenant_user_id'] = tu.id
                    user_dict['is_default'] = tu.is_default
                    user_dict['joined_at'] = tu.created_at.isoformat() if tu.created_at else None
                    users_data.append(user_dict)

            return success_response(data={
                'items': users_data,
                'total': len(users_data)
            })
        except Exception as e:
            current_app.logger.error(f'获取租户用户失败: {str(e)}')
            return error_response(message=f'获取租户用户失败: {str(e)}', code=500)


# ============== 租户成员管理API ==============

@tenant_ns.route('/<int:tenant_id>/members')
class TenantMembersAPI(Resource):
    """租户成员管理API"""

    @require_tenant_member
    def get(self, tenant_id):
        """获取租户成员列表"""
        try:
            # 验证租户存在
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()

            tenant_users = TenantUser.query.filter_by(
                tenant_id=tenant_id,
                is_deleted=False
            ).all()

            members_data = []
            for tu in tenant_users:
                user = User.query.get(tu.user_id)
                if user:
                    member_dict = {
                        'id': tu.id,
                        'user_id': tu.user_id,
                        'username': user.username,
                        'real_name': user.real_name,
                        'email': user.email,
                        'phone': user.phone,
                        'avatar': user.avatar,
                        'role': tu.role,
                        'is_default': tu.is_default,
                        'created_at': tu.created_at.isoformat() if tu.created_at else None
                    }
                    members_data.append(member_dict)

            return success_response(data=members_data)
        except Exception as e:
            current_app.logger.error(f'获取租户成员失败: {str(e)}')
            return error_response(message=f'获取租户成员失败: {str(e)}', code=500)

    @tenant_ns.expect(add_member_model)
    @require_tenant_admin
    def post(self, tenant_id):
        """添加成员到租户（超级管理员或租户管理员）"""
        try:
            data = request.get_json()
            target_user_id = data.get('user_id')
            role = data.get('role', 'member')

            if not target_user_id:
                return error_response(message='用户ID不能为空', code=400)

            # 验证角色
            valid_roles = ['owner', 'admin', 'member']
            if role not in valid_roles:
                return error_response(message=f'无效的角色，必须是: {", ".join(valid_roles)}', code=400)

            # 检查租户是否存在
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()

            # 检查用户是否已在该租户中
            existing = TenantUser.query.filter_by(
                tenant_id=tenant_id,
                user_id=target_user_id,
                is_deleted=False
            ).first()
            if existing:
                return error_response(message='用户已在该租户中', code=400)

            # 检查用户是否存在
            target_user = User.query.get(target_user_id)
            if not target_user:
                return error_response(message='用户不存在', code=404)

            # 权限检查：
            # - 超级管理员可以添加任何角色
            # - 租户管理员只能添加 member 角色
            if not g.is_super_admin:
                if role in ['owner', 'admin']:
                    return error_response(message='只有超级管理员可以添加租户管理员', code=403)

            # 检查租户用户数量限制
            can_add, error_msg = check_tenant_user_limit(tenant_id)
            if not can_add:
                return error_response(message=error_msg, code=400)

            # 添加成员
            tenant_user = TenantUser(
                tenant_id=tenant_id,
                user_id=target_user_id,
                role=role,
                is_default=False
            )

            db.session.add(tenant_user)
            db.session.commit()

            return success_response(data=tenant_user.to_dict(), message='添加成员成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'添加租户成员失败: {str(e)}')
            return error_response(message=f'添加租户成员失败: {str(e)}', code=500)


@tenant_ns.route('/<int:tenant_id>/members/<int:target_user_id>')
class TenantMemberAPI(Resource):
    """租户成员详情API"""

    @require_tenant_admin
    def delete(self, tenant_id, target_user_id):
        """从租户移除成员（超级管理员或租户管理员）"""
        try:
            # 验证租户存在
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()

            # 获取租户用户关联
            tenant_user = TenantUser.query.filter_by(
                tenant_id=tenant_id,
                user_id=target_user_id,
                is_deleted=False
            ).first_or_404()

            # 权限检查：
            # - 超级管理员可以移除任何人
            # - 租户管理员只能移除 member 角色
            if not g.is_super_admin:
                if tenant_user.role in ['owner', 'admin']:
                    return error_response(message='只有超级管理员可以移除租户管理员', code=403)

            # 不能移除自己
            if g.current_user.id == target_user_id:
                return error_response(message='不能移除自己', code=400)

            # 软删除
            tenant_user.is_deleted = True
            db.session.commit()

            return success_response(message='移除成员成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'移除租户成员失败: {str(e)}')
            return error_response(message=f'移除租户成员失败: {str(e)}', code=500)


@tenant_ns.route('/<int:tenant_id>/members/<int:target_user_id>/role')
class TenantMemberRoleAPI(Resource):
    """租户成员角色管理API"""

    @tenant_ns.expect(update_member_role_model)
    @require_super_admin
    def put(self, tenant_id, target_user_id):
        """更新成员角色（仅超级管理员）"""
        try:
            data = request.get_json()
            new_role = data.get('role')

            # 验证角色
            valid_roles = ['owner', 'admin', 'member']
            if new_role not in valid_roles:
                return error_response(message=f'无效的角色，必须是: {", ".join(valid_roles)}', code=400)

            # 验证租户存在
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()

            # 获取租户用户关联
            tenant_user = TenantUser.query.filter_by(
                tenant_id=tenant_id,
                user_id=target_user_id,
                is_deleted=False
            ).first_or_404()

            # 更新角色
            tenant_user.role = new_role
            db.session.commit()

            return success_response(data=tenant_user.to_dict(), message='更新角色成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'更新成员角色失败: {str(e)}')
            return error_response(message=f'更新成员角色失败: {str(e)}', code=500)
