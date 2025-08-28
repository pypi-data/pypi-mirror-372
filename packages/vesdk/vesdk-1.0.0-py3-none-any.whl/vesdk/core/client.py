"""
客户端模块，作为SDK的主要入口点
"""
import requests
import json
from typing import Dict, Any, Optional
from .auth import AuthProvider
from .exceptions import VolcEngineAPIError, AuthenticationError


class VolcEngineClient:
    """火山引擎客户端"""
    
    def __init__(self, access_key_id: str, secret_access_key: str, api_key: str,
                 region: str = "cn-north-1", service: str = "air"):
        
        self.auth_provider = AuthProvider(access_key_id, secret_access_key, service, region)
        self.region = region
        self.service = service
        self.api_key = api_key
        
        # 初始化API模块（延迟初始化）
        self._text_generation = None
        self._image_generation = None
        self._speech_synthesis = None
        self._video_generation = None
        self._memory = None
        self._knowledge = None
    
    @property
    def text_generation(self):
        """文本生成API"""
        if self._text_generation is None:
            from ..api.text_generation import TextGenerationAPI
            self._text_generation = TextGenerationAPI(self)
        return self._text_generation
    
    @property
    def image_generation(self):
        """图像生成API"""
        if self._image_generation is None:
            from ..api.image_generation import ImageGenerationAPI
            self._image_generation = ImageGenerationAPI(self)
        return self._image_generation
    
    @property
    def speech_synthesis(self):
        """语音合成API"""
        if self._speech_synthesis is None:
            from ..api.speech_synthesis import SpeechSynthesisAPI
            self._speech_synthesis = SpeechSynthesisAPI(self)
        return self._speech_synthesis
    
    @property
    def video_generation(self):
        """视频生成API"""
        if self._video_generation is None:
            from ..api.video_generation import VideoGenerationAPI
            self._video_generation = VideoGenerationAPI(self)
        return self._video_generation
    
    @property
    def memory(self):
        """记忆API"""
        if self._memory is None:
            from ..api.memory import MemoryAPI
            self._memory = MemoryAPI(self)
        return self._memory
    
    @property
    def knowledge(self):
        """知识库API"""
        if self._knowledge is None:
            from ..api.knowledge import KnowledgeAPI
            self._knowledge = KnowledgeAPI(self)
        return self._knowledge
    
    def _make_post_request(self, url: str, headers: Dict[str, Any] = None, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            headers: 请求头
            params: 查询参数
            data: 表单数据
            json_data: JSON数据
            
        Returns:
            响应数据
            
        Raises:
            VolcEngineAPIError: API调用错误
        """
        # 合并请求头
        request_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        if headers:
            request_headers.update(headers)
        
        # 发送请求
        try:
            response = requests.post(
                url=url,
                headers=request_headers,
                data=json.dumps(payload),
                timeout=30
            )
            print(response.text)
            # 检查响应状态
            if response.status_code >= 400:
                self._handle_error_response(response)
            
            # 解析响应
            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {"data": response.text}
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise VolcEngineAPIError(f"Request failed: {str(e)}")
    
    def _make_get_request(self, url: str, headers: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        发送GET请求
        
        Args:
            url: 请求URL
            headers: 请求头
            
        Returns:
            响应数据
            
        Raises:
            VolcEngineAPIError: API调用错误
        """
        # 合并请求头
        request_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        if headers:
            request_headers.update(headers)
        
        # 发送请求
        try:
            response = requests.get(
                url=url,
                headers=request_headers,
                timeout=30
            )
            # 检查响应状态
            if response.status_code >= 400:
                self._handle_error_response(response)
            
            # 解析响应
            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {"data": response.text}
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise VolcEngineAPIError(f"Request failed: {str(e)}")
    
    def _make_request_signature(self, method: str, domain: str, path: str, 
                     body: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            domain: 请求domain
            path: 请求路径
            body: 消息体
            params: 查询参数
            
        Returns:
            响应数据
            
        Raises:
            VolcEngineAPIError: API调用错误
        """
        request = self.auth_provider.sign_request(
            method, domain, path, body, params)

        # 发送请求
        try:
            response = requests.request(
                method=request.method,
                url=f"{request.schema}://{request.host}{request.path}",
                headers=request.headers,
                params=params,
                data=request.body,
                timeout=30
            )
            # 检查响应状态
            if response.status_code >= 400:
                self._handle_error_response(response)
            
            # 解析响应
            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {"data": response.text}
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise VolcEngineAPIError(f"Request failed: {str(e)}")
    
    def _handle_error_response(self, response: requests.Response) -> None:
        """处理错误响应"""
        try:
            error_data = response.json()
            message = error_data.get("message", "Unknown error")
            error_code = error_data.get("error_code")
            request_id = response.headers.get("X-Tt-Logid")
        except json.JSONDecodeError:
            message = response.text
            error_code = None
            request_id = response.headers.get("X-Tt-Logid")
        
        # 根据状态码创建特定类型的错误
        if response.status_code == 401:
            raise AuthenticationError(message, response.status_code, error_code, request_id)
        elif response.status_code == 403:
            raise AuthorizationError(message, response.status_code, error_code, request_id)
        elif response.status_code >= 500:
            raise ServerError(message, response.status_code, error_code, request_id)
        else:
            raise VolcEngineAPIError(message, response.status_code, error_code, request_id)