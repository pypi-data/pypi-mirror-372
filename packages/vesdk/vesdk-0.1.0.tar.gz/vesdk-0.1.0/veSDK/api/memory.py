"""
会话记忆API模块
"""
import time
from typing import List, Dict, Any, Optional
from . import BaseAPI


class MemoryAPI(BaseAPI):
    """会话记忆API"""
    
    def create_collection(self, collection_name: str, collection_type: str = "ultimate",
                         cpu_quota: int = 1, description: str = "",
                         builtin_event_types: List[str] = None,
                         builtin_entity_types: List[str] = None,
                         custom_event_type_schemas: List[Dict] = None,
                         custom_entity_type_schemas: List[Dict] = None) -> Dict[str, Any]:
        """
        创建记忆库
        
        Args:
            collection_name: 记忆库名称
            collection_type: 记忆库类型
            cpu_quota: CPU配额
            description: 描述信息
            builtin_event_types: 内置事件类型
            builtin_entity_types: 内置实体类型
            custom_event_type_schemas: 自定义事件类型模式
            custom_entity_type_schemas: 自定义实体类型模式
            
        Returns:
            API响应数据
        """
        # 构建请求URL
        host = "api-knowledgebase.mlp.cn-beijing.volces.com"
        path = "/api/memory/collection/create"
        
        # 构建请求数据
        payload = {
            "CollectionName": collection_name,
            "CollectionType": collection_type,
            "CpuQuota": cpu_quota,
            "Description": description
        }
        
        # 添加可选参数
        if builtin_event_types is not None:
            payload["BuiltinEventTypes"] = builtin_event_types
        
        if builtin_entity_types is not None:
            payload["BuiltinEntityTypes"] = builtin_entity_types
        
        if custom_event_type_schemas is not None:
            payload["CustomEventTypeSchemas"] = custom_event_type_schemas
        
        if custom_entity_type_schemas is not None:
            payload["CustomEntityTypeSchemas"] = custom_entity_type_schemas
        
        # 发送请求
        return self._make_request_signature("POST", host, path, payload)
    
    def add_session(self, collection_name: str, session_id: str,
                    user_id: str = 'user1', assistant_id: str = 'assistant1',
                   messages: List[Dict] = None, metadata: Dict = None,
                   entities: List[Dict] = None) -> Dict[str, Any]:
        """
        添加会话
        
        Args:
            collection_name: 记忆库名称
            session_id: 会话ID
            messages: 消息列表
            metadata: 元数据
            entities: 实体信息
            
        Returns:
            API响应数据
        """
        # 构建请求URL
        host = "api-knowledgebase.mlp.cn-beijing.volces.com"
        path = "/api/memory/session/add"

        # 构建请求数据
        payload = {
                'collection_name': collection_name,
                'session_id': session_id,
                'messages': messages,
                'metadata': {
                    'default_user_id': user_id,
                    'default_assistant_id': assistant_id,
                    'time': int(time.time() * 1000)  # 毫秒时间戳
                }
            }
        
        # 添加可选参数
        if metadata is not None:
            payload["metadata"] = metadata
        
        if entities is not None:
            payload["entities"] = entities
        
        # 发送请求
        return self._make_request_signature("POST", host, path, payload)
    
    def get_session_info(self, collection_name: str, session_id: str) -> Dict[str, Any]:
        """
        获取会话详情
        
        Args:
            collection_name: 记忆库名称
            session_id: 会话ID
            
        Returns:
            API响应数据
        """
        # 构建请求URL
        host = "api-knowledgebase.mlp.cn-beijing.volces.com"
        path = "/api/memory/session/info"
        
        # 构建请求数据
        payload = {
            "collection_name": collection_name,
            "session_id": session_id
        }
        
        # 发送请求
        return self._make_request_signature("POST", host, path, payload)