"""
视觉模型文生图API测试用例
"""
import unittest
from unittest.mock import patch, MagicMock
from ..api.image_generation import ImageGenerationAPI


class TestImageGenerationAPI(unittest.TestCase):
    
    def setUp(self):
        """测试初始化"""
        self.api = ImageGenerationAPI(MagicMock())
    
    @patch('vesdk.api.image_generation.ImageGenerationAPI._make_request')
    def test_generate_image(self, mock_make_request):
        """测试generate_image接口"""
        # 模拟API响应
        mock_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "image_urls": [
                    "https://example.com/image1.png",
                    "https://example.com/image2.png"
                ]
            }
        }
        mock_make_request.return_value = mock_response
        
        # 调用接口
        response = self.api.generate_image(model="your-image-model", prompt="A beautiful landscape")
        
        # 验证结果
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            "POST",
            "https://ark.cn-beijing.volces.com/api/v3/images/generations",
            json_data={
                "model": "your-image-model",
                "prompt": "A beautiful landscape",
                "size": "1024x1024",
                "response_format": "url",
                "guidance_scale": 2.5,
                "watermark": True
            }
        )


if __name__ == '__main__':
    unittest.main()