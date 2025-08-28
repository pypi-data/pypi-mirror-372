"""
知识库API模块
"""
from typing import List, Dict, Any, Optional
from . import BaseAPI


DEFAULT_PREPROCESSING = {
                    'chunking_strategy': 'custom_balance',
                    'chunk_length': 500,
                    'merge_small_chunks': True
                }
                
DEFAULT_INDEX_CONFIG = {
                    'index_type': 'flat',
                    'index_config': {
                        'cpu_quota': 1,
                    }
                }


class KnowledgeAPI(BaseAPI):
    """知识库API"""
    
    def create_collection(self, name: str,
                         description: str = "", version: int = 4,
                         data_type: str = "unstructured_data",
                         preprocessing: Dict = DEFAULT_PREPROCESSING,
                         index_config: Dict = DEFAULT_INDEX_CONFIG) -> Dict[str, Any]:
        """
        创建知识库
        
        Args:
            name: 知识库名称
            description: 描述信息
            version: 版本
            data_type: 数据类型
            preprocessing: 预处理配置
            index_config: 索引配置
            
        Returns:
            API响应数据
        """
        # 构建请求URL
        host = "api-knowledgebase.mlp.cn-beijing.volces.com"
        path = "/api/knowledge/collection/create"
        
        # 构建请求数据
        payload = {
            'name': name,
            'description': description,
            'version': version,  # 旗舰版
            'data_type': data_type,
            'preprocessing': preprocessing,
            'index': index_config
        }
        
        # 发送请求
        return self._make_request_signature("POST", host, path, payload)
    
    def add_document(self, collection_name: str = None, add_type: str = "url",
                    doc_id: str = None, doc_name: str = None,
                    doc_type: str = None, url: str = None, tos_path: str = None,
                    ) -> Dict[str, Any]:
        """
        向知识库添加文档
        
        Args:
            collection_name: 知识库名称
            add_type: 添加方式
            doc_id: 文档ID
            doc_name: 文档名称
            doc_type: 文档类型
            url: 文档URL
            tos_path: TOS路径
            
        Returns:
            API响应数据
        """
        # 构建请求URL
        host = "api-knowledgebase.mlp.cn-beijing.volces.com"
        path = "/api/knowledge/doc/add"
        
        # 构建请求数据
        payload = {
            "add_type": add_type
        }
        payload = {
            'collection_name': collection_name,
            'add_type': add_type,
            'doc_id': doc_id,
            'doc_name': doc_name,
            'doc_type': doc_type, 
        }
        # 添加标识参数
        if add_type == "url":
            payload["url"] = url
        elif add_type == "tos":
            payload["tos_path"] = tos_path
        
        # 发送请求
        return self._make_request_signature("POST", host, path, payload)
    
    def search_knowledge(self, query: str, name: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        知识库语义检索
        
        Args:
            query: 检索文本
            name: 知识库名称
            limit: 检索结果数量
            
        Returns:
            API响应数据
        """
        # 构建请求URL
        host = "api-knowledgebase.mlp.cn-beijing.volces.com"
        path = "/api/knowledge/collection/search_knowledge"
        
        # 构建请求数据
        payload = {
            "name": name,
            "query": query,
            "limit": limit,
        }
        
        # 发送请求
        return self._make_request_signature("POST", host, path, payload)