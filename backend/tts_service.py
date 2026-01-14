"""
AI 瑜珈教練系統 - 語音回饋服務
使用 pyttsx3 實作離線 TTS
"""

import pyttsx3
from pathlib import Path
import logging
from typing import Optional

from config import TTS_LANGUAGE, TTS_RATE, TTS_VOLUME, AUDIO_DIR

# 設定日誌
logger = logging.getLogger(__name__)


class TTSService:
    """文字轉語音服務類別"""
    
    def __init__(self, language=TTS_LANGUAGE, rate=TTS_RATE, volume=TTS_VOLUME):
        """
        初始化 TTS 引擎
        
        Args:
            language: 語言代碼
            rate: 語速
            volume: 音量 (0.0-1.0)
        """
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            # 設定語言（如果支援）
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'chinese' in voice.name.lower() or 'mandarin' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            
            logger.info("TTS 引擎初始化成功")
            
        except Exception as e:
            logger.error(f"TTS 引擎初始化失敗：{e}")
            self.engine = None
    
    def generate_audio(self, text: str, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        生成語音檔案
        
        Args:
            text: 要轉換的文字
            output_path: 輸出檔案路徑（可選，預設自動產生）
        
        Returns:
            Path: 語音檔案路徑或 None
        """
        if not self.engine:
            logger.error("TTS 引擎未初始化")
            return None
        
        try:
            # 如果未指定輸出路徑，自動產生
            if output_path is None:
                import time
                timestamp = int(time.time())
                output_path = AUDIO_DIR / f"feedback_{timestamp}.mp3"
            
            # 確保輸出目錄存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 生成語音
            self.engine.save_to_file(text, str(output_path))
            self.engine.runAndWait()
            
            logger.info(f"語音檔案已生成：{output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"生成語音失敗：{e}")
            return None
    
    def speak(self, text: str):
        """
        即時語音播放（不儲存檔案）
        
        Args:
            text: 要播放的文字
        """
        if not self.engine:
            logger.error("TTS 引擎未初始化")
            return
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"語音播放失敗：{e}")
    
    def stop(self):
        """停止語音播放"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass


# 全域 TTS 實例
_tts_instance = None

def get_tts_service() -> TTSService:
    """
    取得 TTS 服務實例（單例模式）
    
    Returns:
        TTSService: TTS 服務實例
    """
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSService()
    return _tts_instance


if __name__ == "__main__":
    # 測試 TTS
    logging.basicConfig(level=logging.INFO)
    
    tts = TTSService()
    
    # 測試生成語音檔案
    test_text = "很好！標準的 Warrior II 姿勢。保持手臂水平。"
    audio_path = tts.generate_audio(test_text)
    
    if audio_path:
        print(f"語音檔案：{audio_path}")
    
    # 測試即時播放（需要音訊設備）
    # tts.speak(test_text)
