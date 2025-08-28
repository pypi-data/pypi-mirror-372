"""
API模块基类
"""
from typing import Dict, Any


class BaseAPI:
    """API基类"""
    
    def __init__(self, client):
        """
        初始化API基类
        
        Args:
            client: 火山引擎客户端实例
        """
        self.client = client
        
    def _make_request_signature(self, method: str, domain: str, path: str, 
                     params: Dict[str, Any] = None, body: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            domain: 请求domain
            path: 请求路径
            params: 查询参数
            body: 消息体
            
        Returns:
            响应数据
        """
        return self.client._make_request_signature(method, domain, path, params, body)

    def _make_post_request(self, url: str, headers: Dict[str, Any] = None, 
                           payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        发送POST请求
        
        Args:
            url: 请求URL
            headers: 请求头
            payload: 请求体
            
        Returns:
            响应数据
        """
        return self.client._make_post_request(url, headers, payload)
    
    def _make_get_request(self, url: str, headers: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        发送GET请求
        
        Args:
            url: 请求URL
            headers: 请求头
            
        Returns:
            响应数据
        """
        return self.client._make_get_request(url, headers)