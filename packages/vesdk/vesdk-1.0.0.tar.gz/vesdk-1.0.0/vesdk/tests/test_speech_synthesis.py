"""
语音合成API测试用例
"""
import unittest
from unittest.mock import patch, MagicMock
from ..api.speech_synthesis import SpeechSynthesisAPI


class TestSpeechSynthesisAPI(unittest.TestCase):
    
    def setUp(self):
        """测试初始化"""
        self.api = SpeechSynthesisAPI(MagicMock())
    
    @patch('vesdk.api.speech_synthesis.SpeechSynthesisAPI._make_request')
    def test_synthesize_speech(self, mock_make_request):
        """测试synthesize_speech接口"""
        # 模拟API响应
        mock_response = {
            "success": True,
            "code": 0,
            "message": "Success",
            "data": {
                "audio_url": "https://example.com/audio.mp3"
            }
        }
        mock_make_request.return_value = mock_response
        
        # 调用接口
        response = self.api.synthesize_speech(text="Hello, this is a test.", speaker="speaker_name")
        
        # 验证结果
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            "POST",
            "https://openspeech.bytedance.com/api/v3/tts/unidirectional",
            json_data={
                "user": {
                    "uid": "default_user"
                },
                "req_params": {
                    "text": "Hello, this is a test.",
                    "speaker": "speaker_name",
                    "audio_params": {
                        "format": "mp3",
                        "sample_rate": 24000,
                        "speech_rate": 0,
                        "enable_timestamp": False
                    }
                }
            }
        )


if __name__ == '__main__':
    unittest.main()