# vesdk

火山引擎SDK，支持以下功能：

- 大模型文本生成(chat接口)
- 视觉模型文生图接口
- 视觉模式生成视频video接口
- 会话记忆相关接口
- 知识库相关接口

## 安装

```bash
pip install vesdk
```

## 使用示例

```python
from vesdk import VolcEngineClient

# 初始化客户端
client = VolcEngineClient(
    access_key_id="your_access_key_id",
    secret_access_key="your_secret_access_key",
    api_key="your_api_key"
)


# 文本生成示例
response = client.text_generation.chat(
    model="doubao-1-5-pro-32k-250115",
    messages=[
        {"role": "user", "content": "你好！"}
    ]
)

print(response)
```

## 文档

请参考[官方文档](https://www.volcengine.com/docs)获取更多信息。