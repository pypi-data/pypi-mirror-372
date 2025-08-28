"""
视觉模型文生图API模块
"""
from typing import List, Dict, Any, Optional
from . import BaseAPI


class ImageGenerationAPI(BaseAPI):
    """视觉模型文生图API"""
    
    def generate_image(self, model: str, prompt: str, 
                       size: str = "1024x1024", response_format: str = "url",
                       seed: Optional[int] = None, guidance_scale: float = 2.5,
                       watermark: bool = True, **kwargs) -> Dict[str, Any]:
        """
        视觉模型文生图接口
        
        Args:
            model: 模型名称
            prompt: 提示词
            size: 图像尺寸
            response_format: 响应格式
            seed: 随机种子
            guidance_scale: 指导尺度
            watermark: 是否添加水印
            **kwargs: 其他参数
            
        Returns:
            API响应数据
        """
        # 构建请求URL
        url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
        
        # 构建请求数据
        payload = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "response_format": response_format,
            "guidance_scale": guidance_scale,
            "watermark": watermark,
            **kwargs
        }
        
        # 添加可选参数
        if seed is not None:
            payload["seed"] = seed
        
        # 发送请求
        return self._make_post_request(url, {}, payload)