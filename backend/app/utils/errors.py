"""
错误处理工具
"""
from flask import jsonify
from flask_restx import Namespace
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """注册全局错误处理器"""

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """处理HTTP异常"""
        response = {
            'success': False,
            'message': e.description,
            'code': e.code
        }
        return jsonify(response), e.code

    @app.errorhandler(Exception)
    def handle_exception(e):
        """处理未捕获的异常"""
        app.logger.error(f'Unhandled exception: {str(e)}')
        response = {
            'success': False,
            'message': '服务器内部错误',
            'code': 500
        }
        return jsonify(response), 500


def success_response(data=None, message='操作成功', code=200):
    """
    成功响应

    Args:
        data: 响应数据
        message: 响应消息
        code: 状态码

    Returns:
        响应字典
    """
    return {
        'success': True,
        'message': message,
        'data': data,
        'code': code
    }


def error_response(message='操作失败', code=400, data=None):
    """
    错误响应

    Args:
        message: 错误消息
        code: 状态码
        data: 附加数据

    Returns:
        响应字典
    """
    response = {
        'success': False,
        'message': message,
        'code': code
    }
    if data is not None:
        response['data'] = data
    return response


def abort_with_message(namespace, message, code=400):
    """
    中止请求并返回错误消息

    Args:
        namespace: Flask-RESTX命名空间
        message: 错误消息
        code: 状态码
    """
    namespace.abort(code, message)
