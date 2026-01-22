"""
角色管理API
"""
from flask import request, g
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import Role, RoleMenu, UserRole, User, Menu
from app.utils import success_response, error_response
from app.utils.permissions import get_current_user, require_super_admin
from sqlalchemy import or_, text

# 命名空间
role_ns = Namespace('Roles', description='角色管理')

# Swagger模型定义
role_model = role_ns.model('Role', {
    'name': fields.String(required=True, description='角色名称'),
    'code': fields.String(required=True, description='角色代码'),
    'description': fields.String(description='角色描述'),
    'level': fields.Integer(description='权限级别', default=0)
})

assign_menus_model = role_ns.model('AssignMenus', {
    'menu_ids': fields.List(fields.Integer, required=True, description='菜单ID列表')
})

assign_users_model = role_ns.model('AssignUsers', {
    'user_ids': fields.List(fields.Integer, required=True, description='用户ID列表')
})


# ============== 角色管理API ==============

@role_ns.route('')
class RoleListAPI(Resource):
    """角色列表API"""

    def get(self):
        """获取角色列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            keyword = request.args.get('keyword')

            query = Role.query.filter_by(is_deleted=False)

            if keyword:
                query = query.filter(
                    or_(Role.name.contains(keyword), Role.code.contains(keyword))
                )

            pagination = query.order_by(text('level desc, id desc')).paginate(
                page=page, per_page=per_page, error_out=False
            )

            items = []
            for item in pagination.items:
                role_dict = item.to_dict()
                # 获取角色的用户数量
                user_count = UserRole.query.filter_by(role_id=item.id).count()
                role_dict['user_count'] = user_count
                items.append(role_dict)

            return success_response(data={
                'items': items,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            return error_response(message=f'获取角色列表失败: {str(e)}', code=500)

    @require_super_admin
    def post(self):
        """创建角色（仅超级管理员）"""
        try:
            data = request.get_json()

            # 检查角色代码是否已存在
            if Role.query.filter_by(code=data['code'], is_deleted=False).first():
                return error_response(message='角色代码已存在', code=400)

            role = Role(
                name=data.get('name'),
                code=data.get('code'),
                description=data.get('description'),
                role_type=data.get('role_type', 'custom'),
                level=data.get('level', 0),
                created_by=g.current_user.id
            )

            db.session.add(role)
            db.session.commit()

            return success_response(data=role.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'创建角色失败: {str(e)}', code=500)


@role_ns.route('/<int:role_id>')
class RoleAPI(Resource):
    """角色详情API"""

    def get(self, role_id):
        """获取角色详情"""
        try:
            role = Role.query.filter_by(id=role_id, is_deleted=False).first_or_404()
            role_dict = role.to_dict()

            # 获取角色的菜单数量
            menu_count = RoleMenu.query.filter_by(role_id=role_id).count()
            role_dict['menu_count'] = menu_count

            # 获取角色的用户数量
            user_count = UserRole.query.filter_by(role_id=role_id).count()
            role_dict['user_count'] = user_count

            return success_response(data=role_dict)
        except Exception as e:
            return error_response(message=f'获取角色详情失败: {str(e)}', code=500)

    @require_super_admin
    def put(self, role_id):
        """更新角色（仅超级管理员）"""
        try:
            role = Role.query.filter_by(id=role_id, is_deleted=False).first_or_404()
            data = request.get_json()

            # 系统角色不允许修改
            if role.is_system:
                return error_response(message='系统角色不允许修改', code=403)

            # 检查角色代码是否被其他角色使用
            if data.get('code') and data['code'] != role.code:
                if Role.query.filter_by(code=data['code'], is_deleted=False).first():
                    return error_response(message='角色代码已存在', code=400)

            role.name = data.get('name', role.name)
            role.code = data.get('code', role.code)
            role.description = data.get('description', role.description)
            role.level = data.get('level', role.level)
            role.is_enabled = data.get('is_enabled', role.is_enabled)
            role.updated_by = g.current_user.id

            db.session.commit()
            return success_response(data=role.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新角色失败: {str(e)}', code=500)

    @require_super_admin
    def delete(self, role_id):
        """删除角色（仅超级管理员，软删除）"""
        try:
            role = Role.query.filter_by(id=role_id, is_deleted=False).first_or_404()

            # 系统角色不允许删除
            if role.is_system:
                return error_response(message='系统角色不允许删除', code=403)

            # 检查是否有用户使用该角色
            user_count = UserRole.query.filter_by(role_id=role_id).count()
            if user_count > 0:
                return error_response(message=f'该角色下还有 {user_count} 个用户，无法删除', code=400)

            role.is_deleted = True
            role.updated_by = g.current_user.id
            db.session.commit()

            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除角色失败: {str(e)}', code=500)


# ============== 角色菜单API ==============

@role_ns.route('/<int:role_id>/menus')
class RoleMenusAPI(Resource):
    """角色菜单关联API"""

    def get(self, role_id):
        """获取角色的菜单列表"""
        try:
            role = Role.query.filter_by(id=role_id, is_deleted=False).first_or_404()

            # 获取角色关联的菜单ID
            role_menus = RoleMenu.query.filter_by(role_id=role_id).all()
            menu_ids = [rm.menu_id for rm in role_menus]

            # 获取菜单详情
            menus = Menu.query.filter(
                Menu.id.in_(menu_ids),
                Menu.is_deleted == False
            ).order_by(text('sort_order')).all()

            tree = build_menu_tree(menus)
            return success_response(data={'menus': tree, 'menu_ids': menu_ids})
        except Exception as e:
            return error_response(message=f'获取角色菜单失败: {str(e)}', code=500)

    @require_super_admin
    def put(self, role_id):
        """分配菜单给角色（仅超级管理员）"""
        try:
            role = Role.query.filter_by(id=role_id, is_deleted=False).first_or_404()
            data = request.get_json()

            menu_ids = data.get('menu_ids', [])

            # 删除旧的关联
            RoleMenu.query.filter_by(role_id=role_id).delete()

            # 添加新的关联
            for menu_id in menu_ids:
                role_menu = RoleMenu(role_id=role_id, menu_id=menu_id)
                db.session.add(role_menu)

            db.session.commit()
            return success_response(message='分配成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'分配菜单失败: {str(e)}', code=500)


# ============== 角色用户API ==============

@role_ns.route('/<int:role_id>/users')
class RoleUsersAPI(Resource):
    """角色用户关联API"""

    def get(self, role_id):
        """获取角色的用户列表"""
        try:
            role = Role.query.filter_by(id=role_id, is_deleted=False).first_or_404()

            # 获取角色关联的用户
            user_roles = UserRole.query.filter_by(role_id=role_id).all()
            user_ids = [ur.user_id for ur in user_roles]

            # 获取用户详情
            users = User.query.filter(
                User.id.in_(user_ids),
                User.is_deleted == False
            ).all()

            items = [{'id': u.id, 'username': u.username, 'real_name': u.real_name,
                     'email': u.email, 'status': u.status} for u in users]

            return success_response(data={'users': items, 'user_ids': user_ids})
        except Exception as e:
            return error_response(message=f'获取角色用户失败: {str(e)}', code=500)

    @require_super_admin
    def put(self, role_id):
        """分配用户给角色（仅超级管理员）"""
        try:
            role = Role.query.filter_by(id=role_id, is_deleted=False).first_or_404()
            data = request.get_json()

            user_ids = data.get('user_ids', [])

            # 删除旧的关联
            UserRole.query.filter_by(role_id=role_id).delete()

            # 添加新的关联
            for user_id in user_ids:
                user_role = UserRole(role_id=role_id, user_id=user_id)
                db.session.add(user_role)

            db.session.commit()
            return success_response(message='分配成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'分配用户失败: {str(e)}', code=500)


def build_menu_tree(menus):
    """构建菜单树形结构"""
    menu_dict = {m.id: m.to_dict() for m in menus}
    tree = []

    for menu in menus:
        menu_data = menu_dict[menu.id]
        if menu.parent_id and menu.parent_id in menu_dict:
            parent = menu_dict[menu.parent_id]
            if 'children' not in parent:
                parent['children'] = []
            parent['children'].append(menu_data)
        else:
            tree.append(menu_data)

    return tree
