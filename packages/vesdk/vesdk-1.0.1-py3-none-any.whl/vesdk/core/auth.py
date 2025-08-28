"""
认证模块，用于处理火山引擎API的签名和认证
"""
import json
import sys
import requests

from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.Credentials import Credentials
from typing import Dict, Any, Optional


class AuthProvider:
    """火山引擎API认证提供者"""
    
    def __init__(self, access_key_id: str, secret_access_key: str, service: str, region: str):
        """
        初始化认证提供者
        
        Args:
            access_key_id: Access Key ID
            secret_access_key: Secret Access Key
            service: 服务名称
            region: 区域
        """
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.service = service
        self.region = region
    
    def sign_request(self, method: str, domain: str, path: str, body: Optional[Dict] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        为请求生成签名
        
        Args:
            method: HTTP方法
            path: 请求路径
            body: 请求体
            params: 查询参数
            
        Returns:
            包含签名信息的请求头字典
        """
        # 准备请求参数
        if params:
            for key in params:
                if (
                    type(params[key]) == int
                    or type(params[key]) == float
                    or type(params[key]) == bool
                ):
                    params[key] = str(params[key])
                elif type(params[key]) == list:
                    params[key] = ",".join(params[key])
        
        # 创建请求对象
        r = Request()
        r.set_shema("https")
        r.set_method(method)
        r.set_host(domain)
        r.set_path(path)
        r.set_connection_timeout(10)
        r.set_socket_timeout(10)
        
        # 设置请求头
        mheaders = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        r.set_headers(mheaders)
        
        # 设置查询参数和路径
        if params:
            r.set_query(params)
        r.set_path(path)
        
        if body is not None:
            r.set_body(json.dumps(body))
        
        # 生成签名
        credentials = Credentials(self.access_key_id, self.secret_access_key, self.service, self.region)
        SignerV4.sign(r, credentials)
        
        # 返回签名后的请求头
        return r
    