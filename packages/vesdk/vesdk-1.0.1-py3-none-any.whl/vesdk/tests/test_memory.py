"""
会话记忆API测试用例
"""
import unittest
from unittest.mock import patch, MagicMock
from ..api.memory import MemoryAPI


class TestMemoryAPI(unittest.TestCase):
    
    def setUp(self):
        """测试初始化"""
        self.api = MemoryAPI(MagicMock())
    
    @patch('vesdk.api.memory.MemoryAPI._make_request')
    def test_create_collection(self, mock_make_request):
        """测试create_collection接口"""
        # 模拟API响应
        mock_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "collection_name": "test_collection"
            }
        }
        mock_make_request.return_value = mock_response
        
        # 调用接口
        response = self.api.create_collection(collection_name="test_collection")
        
        # 验证结果
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            "POST",
            "https://api-knowledgebase.mlp.cn-beijing.volces.com/api/memory/collection/create",
            json_data={
                "CollectionName": "test_collection",
                "CollectionType": "ultimate",
                "CpuQuota": 1,
                "Description": ""
            }
        )
    
    @patch('vesdk.api.memory.MemoryAPI._make_request')
    def test_add_session(self, mock_make_request):
        """测试add_session接口"""
        # 模拟API响应
        mock_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "session_id": "session_123456"
            }
        }
        mock_make_request.return_value = mock_response
        
        # 调用接口
        messages = [{"role": "user", "content": "Hello"}]
        response = self.api.add_session(collection_name="test_collection", session_id="session_123456", messages=messages)
        
        # 验证结果
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            "POST",
            "https://api-knowledgebase.mlp.cn-beijing.volces.com/api/memory/session/add",
            json_data={
                "collection_name": "test_collection",
                "session_id": "session_123456",
                "messages": messages
            }
        )
    
    @patch('vesdk.api.memory.MemoryAPI._make_request')
    def test_get_session_info(self, mock_make_request):
        """测试get_session_info接口"""
        # 模拟API响应
        mock_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "session_id": "session_123456",
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi, how can I help you?"}
                ]
            }
        }
        mock_make_request.return_value = mock_response
        
        # 调用接口
        response = self.api.get_session_info(collection_name="test_collection", session_id="session_123456")
        
        # 验证结果
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            "POST",
            "https://api-knowledgebase.mlp.cn-beijing.volces.com/api/memory/session/info",
            json_data={
                "collection_name": "test_collection",
                "session_id": "session_123456"
            }
        )


if __name__ == '__main__':
    unittest.main()