"""
视觉模式生成视频API模块
"""
from typing import List, Dict, Any, Optional
from . import BaseAPI


class VideoGenerationAPI(BaseAPI):
    """视觉模式生成视频API"""
    
    def generate_create_video_task(self, model: str, 
                       text_prompt: Optional[str] = None, 
                       first_frame_url: Optional[str] = None, 
                       last_frame_url: Optional[str] = None, 
                       **kwargs) -> Dict[str, Any]:
        """
        创建视频生成任务

        :param model: 使用的模型名称
        :param text_prompt: 文本提示词
        :param first_frame_url: 首帧图片URL
        :param last_frame_url: 尾帧图片URL
        :param kwargs: 其他可选参数
        :return: 任务创建响应
        """
        url = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"

        content = []
        # 添加文本提示
        if text_prompt:
            content.append({
                'type': 'text',
                'text': text_prompt
            })

        # 添加图片
        image_contents = []
        if first_frame_url:
            image_contents.append({
                'type': 'image_url',
                'image_url': {'url': first_frame_url},
                'role': 'first_frame'
            })

        if last_frame_url:
            image_contents.append({
                'type': 'image_url',
                'image_url': {'url': last_frame_url},
                'role': 'last_frame'
            })

        content.extend(image_contents)

        payload = {
            'model': model,
            'content': content,
            **kwargs
        }
        
        # 发送请求
        return self._make_post_request(url, {}, payload)
    
    def get_video_generation_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询视频生成任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            API响应数据
        """
        # 构建请求URL
        url = f"https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"
        
        # 发送请求
        return self._make_get_request(url, {})
    
    def wait_for_video_task_completion(self, task_id: str, timeout: int = 300, interval: int = 5) -> Dict[str, Any]:
        """
        等待视频生成任务完成
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒），默认300秒
            interval: 轮询间隔（秒），默认5秒
            
        Returns:
            最终任务状态
        
        Raises:
            TimeoutError: 任务在超时时间内未完成
        """
        import time
        start_time = time.time()
        
        while True:
            # 检查是否超时
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Video generation task {task_id} did not complete within {timeout} seconds")
            
            # 获取任务状态
            response = self.get_video_generation_task(task_id)
            
            status = response.get('status')

            if status == 'succeeded':
                return response
            elif status == 'failed':
                raise Exception(f'视频生成失败: {response.get("error", "未知错误")}')
            elif status in ['queued', 'running']:
                time.sleep(interval)
            else:
                raise Exception(f'未知任务状态: {status}')
    
    def generate_video(self, model: str, 
                       text_prompt: Optional[str] = None, 
                       first_frame_url: Optional[str] = None, 
                       last_frame_url: Optional[str] = None, 
                       timeout: int = 300, 
                       interval: int = 5,
                       **kwargs) -> Dict[str, Any]:
        """
        创建视频生成任务并等待任务成功

        :param model: 使用的模型名称
        :param text_prompt: 文本提示词
        :param first_frame_url: 首帧图片URL
        :param last_frame_url: 尾帧图片URL
        :param timeout: 等待超时时间（秒），默认300秒
        :param interval: 轮询间隔（秒），默认5秒
        :param kwargs: 其他可选参数
        :return: 最终任务状态
        """
        # 创建视频生成任务
        create_response = self.generate_create_video_task(
            model=model,
            text_prompt=text_prompt,
            first_frame_url=first_frame_url,
            last_frame_url=last_frame_url,
            **kwargs
        )
        
        # 获取任务ID
        task_id = create_response.get('id')
        if not task_id:
            raise Exception('Failed to get task ID from create response')
        
        # 等待任务完成
        return self.wait_for_video_task_completion(task_id, timeout, interval)
