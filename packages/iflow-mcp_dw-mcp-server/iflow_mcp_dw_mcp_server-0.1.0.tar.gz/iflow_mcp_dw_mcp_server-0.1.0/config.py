#!/usr/bin/env python3
"""
语音转文字 MCP 服务器配置文件
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ServerConfig:
    """服务器配置"""
    name: str = "语音转文字服务"
    version: str = "0.1.0"
    description: str = "支持多种音频格式和识别引擎的语音转文字服务"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False


@dataclass
class AudioConfig:
    """音频处理配置"""
    # 支持的输入格式
    supported_input_formats: List[str] = None
    # 支持的输出格式
    supported_output_formats: List[str] = None
    # 支持的语言
    supported_languages: List[str] = None
    # 默认语言
    default_language: str = "zh-CN"
    # 默认引擎
    default_engine: str = "whisper"
    # 最大文件大小 (MB)
    max_file_size: int = 100
    # 临时文件目录
    temp_dir: str = None


@dataclass
class RemoteAPIConfig:
    """远程API配置"""
    # 默认API类型
    default_api_type: str = "bailian"
    # API密钥
    api_key: str = None
    # API地址
    api_url: str = None
    # 请求超时时间 (秒)
    timeout: int = 30
    # 重试次数
    max_retries: int = 3


@dataclass
class GoogleConfig:
    """Google Speech Recognition 配置"""
    # API 密钥 (可选)
    api_key: str = None
    # 请求超时时间 (秒)
    timeout: int = 30
    # 重试次数
    max_retries: int = 3


@dataclass
class SphinxConfig:
    """CMU Sphinx 配置"""
    # 语言模型路径
    language_model_path: str = None
    # 声学模型路径
    acoustic_model_path: str = None
    # 字典路径
    dictionary_path: str = None


class Config:
    """主配置类"""
    
    def __init__(self):
        self.server = ServerConfig()
        self.audio = AudioConfig()
        self.remote_api = RemoteAPIConfig()
        self.google = GoogleConfig()
        self.sphinx = SphinxConfig()
        
        self._load_from_env()
        self._set_defaults()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # 服务器配置
        self.server.name = os.getenv("MCP_SERVER_NAME", self.server.name)
        self.server.version = os.getenv("MCP_SERVER_VERSION", self.server.version)
        self.server.host = os.getenv("MCP_SERVER_HOST", self.server.host)
        self.server.port = int(os.getenv("MCP_SERVER_PORT", str(self.server.port)))
        self.server.debug = os.getenv("MCP_SERVER_DEBUG", "false").lower() == "true"
        
        # 音频配置
        self.audio.default_language = os.getenv("DEFAULT_LANGUAGE", self.audio.default_language)
        self.audio.default_engine = os.getenv("DEFAULT_ENGINE", self.audio.default_engine)
        self.audio.max_file_size = int(os.getenv("MAX_FILE_SIZE", str(self.audio.max_file_size)))
        self.audio.temp_dir = os.getenv("TEMP_DIR", self.audio.temp_dir)
        
        # 远程API配置
        self.remote_api.default_api_type = os.getenv("DEFAULT_API_TYPE", self.remote_api.default_api_type)
        self.remote_api.api_key = os.getenv(f"{self.remote_api.default_api_type.upper()}_API_KEY", self.remote_api.api_key)
        self.remote_api.api_url = os.getenv(f"{self.remote_api.default_api_type.upper()}_API_URL", self.remote_api.api_url)
        self.remote_api.timeout = int(os.getenv("API_TIMEOUT", str(self.remote_api.timeout)))
        self.remote_api.max_retries = int(os.getenv("API_MAX_RETRIES", str(self.remote_api.max_retries)))
        
        # Google 配置
        self.google.api_key = os.getenv("GOOGLE_API_KEY", self.google.api_key)
        self.google.timeout = int(os.getenv("GOOGLE_TIMEOUT", str(self.google.timeout)))
        self.google.max_retries = int(os.getenv("GOOGLE_MAX_RETRIES", str(self.google.max_retries)))
        
        # Sphinx 配置
        self.sphinx.language_model_path = os.getenv("SPHINX_LM_PATH", self.sphinx.language_model_path)
        self.sphinx.acoustic_model_path = os.getenv("SPHINX_AM_PATH", self.sphinx.acoustic_model_path)
        self.sphinx.dictionary_path = os.getenv("SPHINX_DICT_PATH", self.sphinx.dictionary_path)
    
    def _set_defaults(self):
        """设置默认值"""
        # 音频格式
        if self.audio.supported_input_formats is None:
            self.audio.supported_input_formats = [
                "wav", "mp3", "m4a", "flac", "ogg", "aac"
            ]
        
        if self.audio.supported_output_formats is None:
            self.audio.supported_output_formats = [
                "wav", "mp3", "txt", "srt", "vtt"
            ]
        
        if self.audio.supported_languages is None:
            self.audio.supported_languages = [
                "zh-CN", "en-US", "ja-JP", "ko-KR", 
                "fr-FR", "de-DE", "es-ES", "ru-RU"
            ]
        
        # 临时目录
        if self.audio.temp_dir is None:
            self.audio.temp_dir = str(Path.cwd() / "temp")
    
    def get_engine_config(self, engine: str) -> Dict[str, Any]:
        """获取指定引擎的配置"""
        if engine == "remote_api":
            return {
                "api_type": self.remote_api.default_api_type,
                "api_key": self.remote_api.api_key,
                "api_url": self.remote_api.api_url,
                "timeout": self.remote_api.timeout,
                "max_retries": self.remote_api.max_retries
            }
        elif engine == "google":
            return {
                "api_key": self.google.api_key,
                "timeout": self.google.timeout,
                "max_retries": self.google.max_retries
            }
        elif engine == "sphinx":
            return {
                "language_model_path": self.sphinx.language_model_path,
                "acoustic_model_path": self.sphinx.acoustic_model_path,
                "dictionary_path": self.sphinx.dictionary_path
            }
        else:
            return {}
    
    def validate(self) -> List[str]:
        """验证配置"""
        errors = []
        
        # 检查端口
        if not (1 <= self.server.port <= 65535):
            errors.append("端口必须在 1-65535 范围内")
        
        # 检查文件大小限制
        if self.audio.max_file_size <= 0:
            errors.append("最大文件大小必须大于 0")
        
        # 检查默认引擎
        valid_engines = ["remote_api", "google", "sphinx"]
        if self.audio.default_engine not in valid_engines:
            errors.append(f"默认引擎必须是以下之一: {valid_engines}")
        
        # 检查默认语言
        if self.audio.default_language not in self.audio.supported_languages:
            errors.append(f"默认语言必须是支持的语言之一: {self.audio.supported_languages}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "server": {
                "name": self.server.name,
                "version": self.server.version,
                "description": self.server.description,
                "host": self.server.host,
                "port": self.server.port,
                "debug": self.server.debug
            },
            "audio": {
                "supported_input_formats": self.audio.supported_input_formats,
                "supported_output_formats": self.audio.supported_output_formats,
                "supported_languages": self.audio.supported_languages,
                "default_language": self.audio.default_language,
                "default_engine": self.audio.default_engine,
                "max_file_size": self.audio.max_file_size,
                "temp_dir": self.audio.temp_dir
            },
            "remote_api": {
                "default_api_type": self.remote_api.default_api_type,
                "api_key": self.remote_api.api_key,
                "api_url": self.remote_api.api_url,
                "timeout": self.remote_api.timeout,
                "max_retries": self.remote_api.max_retries
            },
            "google": {
                "api_key": self.google.api_key,
                "timeout": self.google.timeout,
                "max_retries": self.google.max_retries
            },
            "sphinx": {
                "language_model_path": self.sphinx.language_model_path,
                "acoustic_model_path": self.sphinx.acoustic_model_path,
                "dictionary_path": self.sphinx.dictionary_path
            }
        }


# 全局配置实例
config = Config()


def get_config() -> Config:
    """获取配置实例"""
    return config


def validate_config() -> bool:
    """验证配置并返回是否有效"""
    errors = config.validate()
    if errors:
        print("配置错误:")
        for error in errors:
            print(f"  - {error}")
        return False
    return True


if __name__ == "__main__":
    # 测试配置
    print("当前配置:")
    import json
    print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
    
    print("\n配置验证:")
    if validate_config():
        print("✅ 配置有效")
    else:
        print("❌ 配置无效") 