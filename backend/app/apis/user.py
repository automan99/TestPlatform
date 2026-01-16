"""
用户管理API
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from app.models import User, Tenant
from app.utils.errors import success_response, error_response
from datetime import datetime
from app import db

# 创建命名空间
user_ns = Namespace('users', description='用户管理接口')

# 定义数据模型
user_model = user_ns.model('User', {
    'id': fields.Integer(description='用户ID'),
    'username': fields.String(required=True, description='用户名'),
    'password': fields.String(description='密码（创建时必填）'),
    'real_name': fields.String(description='真实姓名'),
    'email': fields.String(description='邮箱'),
    'phone': fields.String(description='手机号'),
    'status': fields.String(description='状态'),
    'is_admin': fields.Boolean(description='是否管理员')
})

user_update_model = user_ns.model('UserUpdate', {
    'real_name': fields.String(description='真实姓名'),
    'email': fields.String(description='邮箱'),
    'phone': fields.String(description='手机号'),
    'status': fields.String(description='状态'),
    'is_admin': fields.Boolean(description='是否管理员')
})


@user_ns.route('/')
class UserListAPI(Resource):
    @user_ns.doc('get_users')
    def get(self):
        """获取用户列表"""
        try:
            # 分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            keyword = request.args.get('keyword', '')
            status = request.args.get('status', '')

            # 构建查询
            query = User.query.filter_by(is_deleted=False)

            if keyword:
                query = query.filter(
                    db.or_(
                        User.username.like(f'%{keyword}%'),
                        User.real_name.like(f'%{keyword}%'),
                        User.email.like(f'%{keyword}%')
                    )
                )

            if status:
                query = query.filter_by(status=status)

            # 分页
            pagination = query.order_by(User.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(data={
                'items': [user.to_dict() for user in pagination.items],
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            })
        except Exception as e:
            return error_response(message=f'获取用户列表失败: {str(e)}')

    @user_ns.doc('create_user')
    @user_ns.expect(user_model)
    def post(self):
        """创建用户"""
        try:
            data = request.get_json()

            # 检查用户名是否已存在
            if User.query.filter_by(username=data['username'], is_deleted=False).first():
                return error_response(message='用户名已存在')

            # 创建用户
            user = User(
                username=data['username'],
                real_name=data.get('real_name', ''),
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                status=data.get('status', 'active'),
                is_admin=data.get('is_admin', False)
            )

            # 设置密码
            if 'password' in data:
                user.set_password(data['password'])
            else:
                user.set_password('123456')  # 默认密码

            db.session.add(user)
            db.session.commit()

            return success_response(data=user.to_dict(), message='创建成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'创建用户失败: {str(e)}')


@user_ns.route('/<int:user_id>')
class UserDetailAPI(Resource):
    @user_ns.doc('get_user')
    def get(self, user_id):
        """获取用户详情"""
        try:
            user = User.query.filter_by(id=user_id, is_deleted=False).first()
            if not user:
                return error_response(message='用户不存在', code=404)

            return success_response(data=user.to_dict())
        except Exception as e:
            return error_response(message=f'获取用户详情失败: {str(e)}')

    @user_ns.doc('update_user')
    @user_ns.expect(user_update_model)
    def put(self, user_id):
        """更新用户"""
        try:
            user = User.query.filter_by(id=user_id, is_deleted=False).first()
            if not user:
                return error_response(message='用户不存在', code=404)

            data = request.get_json()

            # 更新字段
            if 'real_name' in data:
                user.real_name = data['real_name']
            if 'email' in data:
                user.email = data['email']
            if 'phone' in data:
                user.phone = data['phone']
            if 'status' in data:
                user.status = data['status']
            if 'is_admin' in data:
                user.is_admin = data['is_admin']

            # 如果提供了新密码
            if 'password' in data and data['password']:
                user.set_password(data['password'])

            user.updated_at = datetime.utcnow()
            db.session.commit()

            return success_response(data=user.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新用户失败: {str(e)}')

    @user_ns.doc('delete_user')
    def delete(self, user_id):
        """删除用户"""
        try:
            user = User.query.filter_by(id=user_id, is_deleted=False).first()
            if not user:
                return error_response(message='用户不存在', code=404)

            # 软删除
            user.is_deleted = True
            user.updated_at = datetime.utcnow()
            db.session.commit()

            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除用户失败: {str(e)}')


@user_ns.route('/<int:user_id>/reset-password')
class UserResetPasswordAPI(Resource):
    @user_ns.doc('reset_password')
    def post(self, user_id):
        """重置用户密码"""
        try:
            user = User.query.filter_by(id=user_id, is_deleted=False).first()
            if not user:
                return error_response(message='用户不存在', code=404)

            # 重置为默认密码
            user.set_password('123456')
            user.updated_at = datetime.utcnow()
            db.session.commit()

            return success_response(message='密码已重置为: 123456')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'重置密码失败: {str(e)}')
