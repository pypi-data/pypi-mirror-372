"""
视觉模式生成视频API测试用例
"""
import unittest
from unittest.mock import patch, MagicMock
from ..api.video_generation import VideoGenerationAPI


class TestVideoGenerationAPI(unittest.TestCase):
    
    def setUp(self):
        """测试初始化"""
        self.api = VideoGenerationAPI(MagicMock())
    
    @patch('vesdk.api.video_generation.VideoGenerationAPI._make_request')
    def test_generate_create_video_task(self, mock_make_request):
        """测试generate_create_video_task接口"""
        # 模拟API响应
        mock_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "task_id": "task_123456"
            }
        }
        mock_make_request.return_value = mock_response
        
        # 调用接口
        response = self.api.generate_create_video_task(model="doubao-seedance-1-0-pro-250528", text_prompt="A beautiful landscape")
        
        # 验证结果
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            "POST",
            "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks",
            json_data={
                "model": "doubao-seedance-1-0-pro-250528",
                "content": [{
                    "type": "text",
                    "text": "A beautiful landscape"
                }]
            }
        )
    
    @patch('vesdk.api.video_generation.VideoGenerationAPI._make_request')
    def test_generate_create_video_task_with_frames(self, mock_make_request):
        """测试包含首帧和尾帧图片URL的视频生成接口"""
        # 模拟API响应
        mock_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "task_id": "task_123456"
            }
        }
        mock_make_request.return_value = mock_response
        
        # 调用接口
        response = self.api.generate_create_video_task(
            model="doubao-seedance-1-0-pro-250528",
            text_prompt="A beautiful landscape",
            first_frame_url="https://example.com/first_frame.jpg",
            last_frame_url="https://example.com/last_frame.jpg"
        )
        
        # 验证结果
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            "POST",
            "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks",
            json_data={
                "model": "doubao-seedance-1-0-pro-250528",
                "content": [
                    {
                        "type": "text",
                        "text": "A beautiful landscape"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/first_frame.jpg"},
                        "role": "first_frame"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/last_frame.jpg"},
                        "role": "last_frame"
                    }
                ]
            }
        )
    
    @patch('vesdk.api.video_generation.VideoGenerationAPI._make_request')
    def test_get_video_generation_task(self, mock_make_request):
        """测试get_video_generation_task接口"""
        # 模拟API响应
        mock_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "task_id": "task_123456",
                "status": "completed",
                "video_url": "https://example.com/video.mp4"
            }
        }
        mock_make_request.return_value = mock_response
        
        # 调用接口
        response = self.api.get_video_generation_task(task_id="task_123456")
        
        # 验证结果
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            "GET",
            "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/task_123456"
        )
    
    @patch('vesdk.api.video_generation.VideoGenerationAPI.get_video_generation_task')
    def test_wait_for_video_task_completion_success(self, mock_get_task):
        """测试wait_for_video_task_completion方法成功完成任务"""
        # 模拟API响应序列
        mock_responses = [
            {"success": True, "code": 0, "message": "Success", "data": {"task_id": "task_123456", "status": "processing"}},
            {"success": True, "code": 0, "message": "Success", "data": {"task_id": "task_123456", "status": "processing"}},
            {"success": True, "code": 0, "message": "Success", "data": {"task_id": "task_123456", "status": "completed", "video_url": "https://example.com/video.mp4"}}
        ]
        mock_get_task.side_effect = mock_responses
        
        # 调用接口
        response = self.api.wait_for_video_task_completion("task_123456", timeout=30, interval=1)
        
        # 验证结果
        self.assertEqual(response, mock_responses[2])
        self.assertEqual(mock_get_task.call_count, 3)
    
    @patch('vesdk.api.video_generation.VideoGenerationAPI.get_video_generation_task')
    def test_wait_for_video_task_completion_failed(self, mock_get_task):
        """测试wait_for_video_task_completion方法任务失败"""
        # 模拟API响应
        mock_response = {"success": True, "code": 0, "message": "Success", "data": {"task_id": "task_123456", "status": "failed"}}
        mock_get_task.return_value = mock_response
        
        # 验证抛出异常
        with self.assertRaises(Exception) as context:
            self.api.wait_for_video_task_completion("task_123456", timeout=30, interval=1)
        
        self.assertTrue("Video generation task task_123456 failed" in str(context.exception))
    
    @patch('vesdk.api.video_generation.VideoGenerationAPI.wait_for_video_task_completion')
    @patch('vesdk.api.video_generation.VideoGenerationAPI.generate_create_video_task')
    def test_generate_video(self, mock_generate_create, mock_wait_for_completion):
        """测试generate_video接口"""
        # 模拟API响应
        mock_create_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "task_id": "task_123456"
            }
        }
        mock_generate_create.return_value = mock_create_response
        
        mock_completion_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "task_id": "task_123456",
                "status": "completed",
                "video_url": "https://example.com/video.mp4"
            }
        }
        mock_wait_for_completion.return_value = mock_completion_response
        
        # 调用接口
        response = self.api.generate_video(model="doubao-seedance-1-0-pro-250528", text_prompt="A beautiful landscape")
        
        # 验证结果
        self.assertEqual(response, mock_completion_response)
        mock_generate_create.assert_called_once_with(
            model="doubao-seedance-1-0-pro-250528",
            text_prompt="A beautiful landscape"
        )
        mock_wait_for_completion.assert_called_once_with("task_123456", 300, 5)


if __name__ == '__main__':
    unittest.main()