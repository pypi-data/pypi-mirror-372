"""
知识库API测试用例
"""
import unittest
from unittest.mock import patch, MagicMock
from ..api.knowledge import KnowledgeAPI


class TestKnowledgeAPI(unittest.TestCase):
    
    def setUp(self):
        """测试初始化"""
        self.api = KnowledgeAPI(MagicMock())
    
    @patch('vesdk.api.knowledge.KnowledgeAPI._make_request')
    def test_create_collection(self, mock_make_request):
        """测试create_collection接口"""
        # 模拟API响应
        mock_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "name": "test_knowledge_base"
            }
        }
        mock_make_request.return_value = mock_response
        
        # 调用接口
        response = self.api.create_collection(name="test_knowledge_base")
        
        # 验证结果
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            "POST",
            "https://api-knowledgebase.mlp.cn-beijing.volces.com/api/knowledge/collection/create",
            json_data={
                "name": "test_knowledge_base",
                "project": "default",
                "description": "",
                "version": 4,
                "data_type": "unstructured_data"
            }
        )
    
    @patch('vesdk.api.knowledge.KnowledgeAPI._make_request')
    def test_add_document(self, mock_make_request):
        """测试add_document接口"""
        # 模拟API响应
        mock_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "doc_id": "doc_123456"
            }
        }
        mock_make_request.return_value = mock_response
        
        # 调用接口
        response = self.api.add_document(collection_name="test_knowledge_base", url="https://example.com/document.pdf")
        
        # 验证结果
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            "POST",
            "https://api-knowledgebase.mlp.cn-beijing.volces.com/api/knowledge/doc/add",
            json_data={
                "collection_name": "test_knowledge_base",
                "project": "default",
                "add_type": "url",
                "url": "https://example.com/document.pdf"
            }
        )
    
    @patch('vesdk.api.knowledge.KnowledgeAPI._make_request')
    def test_search_knowledge(self, mock_make_request):
        """测试search_knowledge接口"""
        # 模拟API响应
        mock_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "results": [
                    {
                        "doc_id": "doc_123456",
                        "content": "This is a test document."
                    }
                ]
            }
        }
        mock_make_request.return_value = mock_response
        
        # 调用接口
        response = self.api.search_knowledge(query="test query", name="test_knowledge_base")
        
        # 验证结果
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            "POST",
            "https://api-knowledgebase.mlp.cn-beijing.volces.com/api/knowledge/collection/search_knowledge",
            json_data={
                "query": "test query",
                "name": "test_knowledge_base",
                "project": "default",
                "limit": 10,
                "dense_weight": 0.5
            }
        )


if __name__ == '__main__':
    unittest.main()