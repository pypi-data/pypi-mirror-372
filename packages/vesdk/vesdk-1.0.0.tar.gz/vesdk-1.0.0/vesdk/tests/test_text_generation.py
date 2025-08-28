"""
文本生成API测试用例
"""
import unittest
from unittest.mock import patch, MagicMock
from ..api.text_generation import TextGenerationAPI


class TestTextGenerationAPI(unittest.TestCase):
    
    def setUp(self):
        """测试初始化"""
        self.api = TextGenerationAPI(MagicMock())
    
    @patch('vesdk.api.text_generation.TextGenerationAPI._make_request')
    def test_chat(self, mock_make_request):
        """测试chat接口"""
        # 模拟API响应
        mock_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Hello, how can I help you?"
                        }
                    }
                ]
            }
        }
        mock_make_request.return_value = mock_response
        
        # 调用接口
        messages = [{"role": "user", "content": "Hello"}]
        response = self.api.chat(model="your-model-name", messages=messages)
        
        # 验证结果
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            "POST",
            "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            json_data={
                "model": "your-model-name",
                "messages": messages,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1024,
                "stream": False
            }
        )


if __name__ == '__main__':
    unittest.main()