"""
异常处理模块，用于处理火山引擎API调用中的错误
"""

class VolcEngineAPIError(Exception):
    """火山引擎API错误基类"""
    
    def __init__(self, message: str, status_code: int = None, error_code: str = None, 
                 request_id: str = None, raw_response: str = None):
        """
        初始化API错误
        
        Args:
            message: 错误消息
            status_code: HTTP状态码
            error_code: 错误代码
            request_id: 请求ID
            raw_response: 原始响应内容
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.request_id = request_id
        self.raw_response = raw_response
    
    def __str__(self):
        """返回错误的字符串表示"""
        error_str = f"VolcEngineAPIError: {self.message}"
        if self.status_code:
            error_str += f" (Status: {self.status_code})"
        if self.error_code:
            error_str += f" (Error Code: {self.error_code})"
        if self.request_id:
            error_str += f" (Request ID: {self.request_id})"
        return error_str


class AuthenticationError(VolcEngineAPIError):
    """认证错误"""
    pass


class AuthorizationError(VolcEngineAPIError):
    """授权错误"""
    pass


class RequestError(VolcEngineAPIError):
    """请求错误"""
    pass


class ServerError(VolcEngineAPIError):
    """服务器错误"""
    pass