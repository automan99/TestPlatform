"""
加密解密工具模块
用于敏感数据（如 Git 凭证）的加密存储
"""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import current_app


class CryptoManager:
    """加密管理器"""

    def __init__(self, key=None):
        """
        初始化加密管理器

        Args:
            key: 加密密钥，如果为 None 则从配置中获取
        """
        if key is None:
            key = self._get_encryption_key()
        self.cipher = Fernet(key)

    def _get_encryption_key(self):
        """
        从配置获取或生成加密密钥

        Returns:
            bytes: Fernet 格式的加密密钥
        """
        # 尝试从配置获取
        key_str = current_app.config.get('ENCRYPTION_KEY')
        if key_str:
            # 如果是 base64 编码的密钥，直接使用
            try:
                return base64.urlsafe_b64decode(key_str.encode())
            except Exception:
                pass

        # 如果配置中有密钥种子，派生密钥
        seed = current_app.config.get('ENCRYPTION_KEY_SEED', 'default-seed-change-in-production')
        salt = b'testp-skill-repo'  # 固定盐值用于密钥派生
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(seed.encode()))
        return key

    def encrypt(self, data: str) -> str:
        """
        加密字符串

        Args:
            data: 要加密的字符串

        Returns:
            str: Base64 编码的加密结果
        """
        if not data:
            return ''
        encrypted = self.cipher.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        """
        解密字符串

        Args:
            encrypted_data: 加密的字符串

        Returns:
            str: 解密后的原始字符串

        Raises:
            ValueError: 解密失败
        """
        if not encrypted_data:
            return ''
        try:
            encrypted = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f'解密失败: {str(e)}')


# 全局实例
_crypto_manager = None


def get_crypto_manager():
    """
    获取加密管理器实例

    Returns:
        CryptoManager: 加密管理器单例
    """
    global _crypto_manager
    if _crypto_manager is None:
        _crypto_manager = CryptoManager()
    return _crypto_manager


def encrypt_data(data: str) -> str:
    """
    加密数据的便捷函数

    Args:
        data: 要加密的字符串

    Returns:
        str: 加密后的字符串
    """
    return get_crypto_manager().encrypt(data)


def decrypt_data(encrypted_data: str) -> str:
    """
    解密数据的便捷函数

    Args:
        encrypted_data: 加密的字符串

    Returns:
        str: 解密后的字符串
    """
    return get_crypto_manager().decrypt(encrypted_data)


def generate_fernet_key() -> str:
    """
    生成新的 Fernet 密钥

    Returns:
        str: Base64 编码的密钥
    """
    return Fernet.generate_key().decode('utf-8')
