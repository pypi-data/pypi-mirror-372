"""
大模型文本生成API模块
"""
from typing import List, Dict, Any, Optional
from . import BaseAPI


class TextGenerationAPI(BaseAPI):
    """大模型文本生成API"""
    
    def chat(self, model: str, messages: List[Dict[str, str]], 
             temperature: float = 0.7, top_p: float = 0.9,
             max_tokens: int = 1024, stream: bool = False,
             **kwargs) -> Dict[str, Any]:
        """
        文本生成chat接口
        
        Args:
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            top_p: Top-P参数
            max_tokens: 最大token数
            stream: 是否流式输出
            **kwargs: 其他参数
            
        Returns:
            API响应数据
        """
        # 构建请求URL
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        
        # 构建请求数据
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": stream,
            **kwargs
        }
        
        # 发送请求
        return self._make_post_request(url, {}, payload)