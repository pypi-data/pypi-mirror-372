"""用户存储管理模块"""

import os
import json
import time
from typing import Optional
from pathlib import Path


class UserStorage:
    """用户信息存储管理类"""
    
    def __init__(self):
        """初始化用户存储"""
        # 使用用户主目录下的 .bigquant 文件夹存储用户信息
        self.storage_dir = Path.home() / ".bigquant"
        self.storage_file = self.storage_dir / "user_info.json"
        
        # 确保存储目录存在
        self.storage_dir.mkdir(exist_ok=True)
    
    
    def get_user_id(self) -> Optional[str]:
        """
        获取存储的用户ID
        
        Returns:
            用户ID，如果不存在或已过期则返回None
        """
        try:
            if not self.storage_file.exists():
                return None
            
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            # 检查是否过期
            current_time = time.time()
            if current_time > user_data.get("expire_time", 0):
                # 已过期，删除文件
                self.clear_user_info()
                return None
            
            return user_data.get("user_id")
            
        except Exception:
            return None
    
    def get_user_info(self) -> Optional[dict]:
        """
        获取完整的用户信息
        
        Returns:
            用户信息字典，如果不存在或已过期则返回None
        """
        try:
            if not self.storage_file.exists():
                return None
            
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            # 检查是否过期
            current_time = time.time()
            if current_time > user_data.get("expire_time", 0):
                # 已过期，删除文件
                self.clear_user_info()
                return None
            
            return user_data
            
        except Exception:
            return None
    
    
    def is_logged_in(self) -> bool:
        """检查用户是否已登录且未过期"""
        return self.get_user_id() is not None
    
    def get_token(self) -> Optional[str]:
        """
        获取存储的token
        
        Returns:
            token，如果不存在或已过期则返回None
        """
        try:
            if not self.storage_file.exists():
                return None
            
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            # 检查是否过期
            current_time = time.time()
            if current_time > user_data.get("expire_time", 0):
                # 已过期，删除文件
                self.clear_user_info()
                return None
            
            return user_data.get("token")
            
        except Exception:
            return None
    
    
    
    def get_auth_type(self) -> Optional[str]:
        """
        获取认证类型
        
        Returns:
            认证类型 ("password"、"keypair" 或 "aksk")，如果不存在或已过期则返回None
        """
        try:
            user_data = self.get_user_info()
            if not user_data:
                return None
            
            return user_data.get("auth_type", "password")  # 默认为password认证
            
        except Exception:
            return None
    
    def get_access_key(self) -> Optional[str]:
        """
        获取存储的Access Key
        
        Returns:
            Access Key，如果不存在或已过期或不是aksk认证则返回None
        """
        try:
            user_data = self.get_user_info()
            if not user_data:
                return None
            
            # 只有aksk认证才返回access key
            if user_data.get("auth_type") == "aksk":
                return user_data.get("access_key")
            
            return None
            
        except Exception:
            return None
    
    def get_secret_key(self) -> Optional[str]:
        """
        获取存储的Secret Key
        
        Returns:
            Secret Key，如果不存在或已过期或不是aksk认证则返回None
        """
        try:
            user_data = self.get_user_info()
            if not user_data:
                return None
            
            # 只有aksk认证才返回secret key
            if user_data.get("auth_type") == "aksk":
                return user_data.get("secret_key")
            
            return None
            
        except Exception:
            return None
    
user_storage = UserStorage()


