"""
菜单权限管理API
"""
from flask import request, g
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import Menu, Role, RoleMenu, UserRole, User
from app.utils import success_response, error_response
from app.utils.permissions import get_current_user, require_super_admin
from sqlalchemy import or_, text

# 命名空间
menu_ns = Namespace('Menus', description='菜单权限管理')

# Swagger模型定义
menu_model = menu_ns.model('Menu', {
    'name': fields.String(required=True, description='菜单名称'),
    'code': fields.String(required=True, description='菜单代码'),
    'title': fields.String(description='菜单标题'),
    'parent_id': fields.Integer(description='父菜单ID'),
    'path': fields.String(description='路由路径'),
    'component': fields.String(description='组件路径'),
    'icon': fields.String(description='图标'),
    'type': fields.String(description='类型: menu/button/link', default='menu'),
    'sort_order': fields.Integer(description='排序号', default=0),
    'is_visible': fields.Boolean(description='是否可见', default=True),
    'permission': fields.String(description='权限标识')
})

role_model = menu_ns.model('Role', {
    'name': fields.String(required=True, description='角色名称'),
    'code': fields.String(required=True, description='角色代码'),
    'description': fields.String(description='角色描述'),
    'level': fields.Integer(description='权限级别', default=0)
})

assign_menus_model = menu_ns.model('AssignMenus', {
    'menu_ids': fields.List(fields.Integer, required=True, description='菜单ID列表')
})

assign_role_model = menu_ns.model('AssignRole', {
    'user_id': fields.Integer(required=True, description='用户ID'),
    'role_id': fields.Integer(required=True, description='角色ID')
})


# ============== 菜单管理API ==============

@menu_ns.route('')
class MenuListAPI(Resource):
    """菜单列表API"""

    def get(self):
        """获取菜单列表（树形结构）"""
        try:
            user = get_current_user()
            if not user:
                return error_response(message='未登录或登录已过期', code=401)

            # 获取用户可访问的菜单
            if user.is_super_admin():
                # 超级管理员可以访问所有菜单（包括不可见的父菜单）
                menus = Menu.query.filter_by(is_deleted=False).order_by(text('sort_order')).all()
            else:
                # 普通用户只能访问有权限的菜单（需要包含父菜单以显示树形结构）
                # 先获取用户有权限的菜单ID
                accessible_menu_ids = db.session.query(Menu.id).join(
                    RoleMenu, RoleMenu.menu_id == Menu.id
                ).join(
                    UserRole, UserRole.role_id == RoleMenu.role_id
                ).filter(
                    UserRole.user_id == user.id,
                    Menu.is_deleted == False,
                    Menu.is_enabled == True
                ).all()
                accessible_menu_ids = [m[0] for m in accessible_menu_ids]

                # 获取所有可访问的菜单及其父菜单
                menus = []
                processed_ids = set()

                for menu_id in accessible_menu_ids:
                    if menu_id in processed_ids:
                        continue
                    # 递归获取菜单及其所有父菜单
                    current_menu = Menu.query.get(menu_id)
                    while current_menu and current_menu.id not in processed_ids:
                        menus.append(current_menu)
                        processed_ids.add(current_menu.id)
                        if current_menu.parent_id:
                            current_menu = Menu.query.get(current_menu.parent_id)
                        else:
                            break

                # 按sort_order排序
                menus = sorted(menus, key=lambda m: m.sort_order or 0)

            # 构建树形结构
            tree = build_menu_tree(menus)
            return success_response(data=tree)
        except Exception as e:
            return error_response(message=f'获取菜单列表失败: {str(e)}', code=500)

    @require_super_admin
    def post(self):
        """创建菜单（仅超级管理员）"""
        try:
            data = request.get_json()

            # 检查菜单代码是否已存在
            if Menu.query.filter_by(code=data['code'], is_deleted=False).first():
                return error_response(message='菜单代码已存在', code=400)

            menu = Menu(
                name=data.get('name'),
                code=data.get('code'),
                title=data.get('title'),
                parent_id=data.get('parent_id'),
                path=data.get('path'),
                component=data.get('component'),
                redirect=data.get('redirect'),
                icon=data.get('icon'),
                type=data.get('type', 'menu'),
                sort_order=data.get('sort_order', 0),
                is_visible=data.get('is_visible', True),
                is_enabled=data.get('is_enabled', True),
                is_cached=data.get('is_cached', False),
                permission=data.get('permission'),
                created_by=g.current_user.id
            )

            db.session.add(menu)
            db.session.commit()

            return success_response(data=menu.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'创建菜单失败: {str(e)}', code=500)


@menu_ns.route('/<int:menu_id>')
class MenuAPI(Resource):
    """菜单详情API"""

    @require_super_admin
    def get(self, menu_id):
        """获取菜单详情"""
        try:
            menu = Menu.query.filter_by(id=menu_id, is_deleted=False).first_or_404()
            return success_response(data=menu.to_dict(include_children=True))
        except Exception as e:
            return error_response(message=f'获取菜单详情失败: {str(e)}', code=500)

    @require_super_admin
    def put(self, menu_id):
        """更新菜单（仅超级管理员）"""
        try:
            menu = Menu.query.filter_by(id=menu_id, is_deleted=False).first_or_404()
            data = request.get_json()

            # 检查菜单代码是否被其他菜单使用
            if data.get('code') and data['code'] != menu.code:
                if Menu.query.filter_by(code=data['code'], is_deleted=False).first():
                    return error_response(message='菜单代码已存在', code=400)

            menu.name = data.get('name', menu.name)
            menu.code = data.get('code', menu.code)
            menu.title = data.get('title', menu.title)
            menu.parent_id = data.get('parent_id', menu.parent_id)
            menu.path = data.get('path', menu.path)
            menu.component = data.get('component', menu.component)
            menu.redirect = data.get('redirect', menu.redirect)
            menu.icon = data.get('icon', menu.icon)
            menu.type = data.get('type', menu.type)
            menu.sort_order = data.get('sort_order', menu.sort_order)
            menu.is_visible = data.get('is_visible', menu.is_visible)
            menu.is_enabled = data.get('is_enabled', menu.is_enabled)
            menu.is_cached = data.get('is_cached', menu.is_cached)
            menu.permission = data.get('permission', menu.permission)
            menu.updated_by = g.current_user.id

            db.session.commit()
            return success_response(data=menu.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新菜单失败: {str(e)}', code=500)

    @require_super_admin
    def delete(self, menu_id):
        """删除菜单（仅超级管理员，软删除）"""
        try:
            menu = Menu.query.filter_by(id=menu_id, is_deleted=False).first_or_404()

            # 检查是否有子菜单
            if menu.children.filter_by(is_deleted=False).count() > 0:
                return error_response(message='该菜单下有子菜单，无法删除', code=400)

            menu.is_deleted = True
            menu.updated_by = g.current_user.id
            db.session.commit()

            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除菜单失败: {str(e)}', code=500)


# ============== 角色管理API ==============

@menu_ns.route('/roles')
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

            items = [item.to_dict() for item in pagination.items]

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


@menu_ns.route('/roles/<int:role_id>')
class RoleAPI(Resource):
    """角色详情API"""

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

            role.is_deleted = True
            role.updated_by = g.current_user.id
            db.session.commit()

            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除角色失败: {str(e)}', code=500)


@menu_ns.route('/roles/<int:role_id>/menus')
class RoleMenusAPI(Resource):
    """角色菜单关联API"""

    def get(self, role_id):
        """获取角色的菜单列表"""
        try:
            role = Role.query.filter_by(id=role_id, is_deleted=False).first_or_404()

            # 获取角色关联的菜单
            role_menus = RoleMenu.query.filter_by(role_id=role_id).all()
            menu_ids = [rm.menu_id for rm in role_menus]

            # 获取菜单详情
            menus = Menu.query.filter(
                Menu.id.in_(menu_ids),
                Menu.is_deleted == False
            ).order_by(text('sort_order')).all()

            tree = build_menu_tree(menus)
            return success_response(data=tree)
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


# ============== 用户菜单API ==============

@menu_ns.route('/user/menus')
class UserMenusAPI(Resource):
    """用户菜单API"""

    def get(self):
        """获取当前用户的菜单列表"""
        try:
            user = get_current_user()
            if not user:
                return error_response(message='未登录或登录已过期', code=401)

            # 获取用户可访问的可见菜单
            if user.is_super_admin():
                # 超级管理员可以访问所有可见菜单
                menus = Menu.query.filter_by(
                    is_deleted=False,
                    is_visible=True
                ).order_by(text('sort_order')).all()
            else:
                # 普通用户通过角色获取菜单
                menus = Menu.query.join(
                    RoleMenu, RoleMenu.menu_id == Menu.id
                ).join(
                    UserRole, UserRole.role_id == RoleMenu.role_id
                ).filter(
                    UserRole.user_id == user.id,
                    Menu.is_deleted == False,
                    Menu.is_enabled == True,
                    Menu.is_visible == True
                ).order_by(text('sort_order')).all()

            # 收集需要添加的不可见父菜单
            menu_ids_to_add = {m.id for m in menus}
            additional_menus = []

            for menu in menus:
                current = menu
                while current.parent_id:
                    parent = Menu.query.filter_by(
                        id=current.parent_id,
                        is_deleted=False
                    ).first()
                    if parent and parent.id not in menu_ids_to_add:
                        menu_ids_to_add.add(parent.id)
                        additional_menus.append(parent)
                    elif not parent:
                        break
                    current = parent if parent else None

            # 添加父菜单并排序
            menus.extend(additional_menus)
            menus = sorted(menus, key=lambda m: m.sort_order or 0)

            # 构建树形结构
            tree = build_menu_tree(menus)
            return success_response(data=tree)
        except Exception as e:
            return error_response(message=f'获取用户菜单失败: {str(e)}', code=500)


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
