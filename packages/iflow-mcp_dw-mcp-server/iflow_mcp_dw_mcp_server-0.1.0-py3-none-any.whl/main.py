#!/usr/bin/env python3
"""
语音转文字 MCP 服务器

这个服务器提供多种语音转文字功能，支持不同的音频格式和识别引擎。
"""

import asyncio
import os
import tempfile
import wave
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import requests
import base64

from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field
import speech_recognition as sr
from pydub import AudioSegment


# 创建 MCP 服务器
mcp = FastMCP(
    "语音转文字服务",
    dependencies=["speechrecognition", "pydub", "requests"]
)


# 数据模型
class TranscriptionResult(BaseModel):
    """语音转文字结果"""
    text: str = Field(description="转写的文本内容")
    confidence: float = Field(description="识别置信度", ge=0.0, le=1.0)
    language: str = Field(description="识别的语言")
    duration: float = Field(description="音频时长（秒）")
    segments: List[Dict[str, Any]] = Field(description="分段信息", default_factory=list)


class AudioInfo(BaseModel):
    """音频文件信息"""
    format: str = Field(description="音频格式")
    duration: float = Field(description="时长（秒）")
    sample_rate: int = Field(description="采样率")
    channels: int = Field(description="声道数")
    file_size: int = Field(description="文件大小（字节）")


class SupportedFormats(BaseModel):
    """支持的音频格式"""
    input_formats: List[str] = Field(description="支持的输入格式")
    output_formats: List[str] = Field(description="支持的输出格式")
    languages: List[str] = Field(description="支持的语言")


# 工具函数
def convert_audio_format(input_path: str, output_path: str, target_format: str = "wav") -> str:
    """转换音频格式"""
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format=target_format)
    return output_path


def get_audio_info(file_path: str) -> AudioInfo:
    """获取音频文件信息"""
    audio = AudioSegment.from_file(file_path)
    return AudioInfo(
        format=audio.format_name,
        duration=len(audio) / 1000.0,  # 转换为秒
        sample_rate=audio.frame_rate,
        channels=audio.channels,
        file_size=os.path.getsize(file_path)
    )


# MCP 工具
@mcp.tool()
async def transcribe_audio_file(
    file_path: str,
    language: str = "zh-CN",
    engine: str = "google",
    ctx: Context = None
) -> TranscriptionResult:
    """
    使用指定引擎转写音频文件
    
    Args:
        file_path: 音频文件路径
        language: 语言代码 (zh-CN, en-US, ja-JP 等)
        engine: 识别引擎 (google, sphinx, remote_api)
        ctx: MCP 上下文
    """
    if ctx:
        await ctx.info(f"开始转写音频文件: {file_path}")
        await ctx.info(f"使用引擎: {engine}, 语言: {language}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"音频文件不存在: {file_path}")
    
    # 获取音频信息
    audio_info = get_audio_info(file_path)
    
    if ctx:
        await ctx.report_progress(progress=0.1, total=1.0, message="正在分析音频文件...")
    
    # 根据引擎选择转写方法
    if engine == "remote_api":
        return await _transcribe_with_remote_api(file_path, language, ctx)
    elif engine == "google":
        return await _transcribe_with_google(file_path, language, ctx)
    elif engine == "sphinx":
        return await _transcribe_with_sphinx(file_path, language, ctx)
    else:
        raise ValueError(f"不支持的引擎: {engine}")


@mcp.tool()
async def transcribe_audio_data(
    audio_data: bytes,
    format: str = "wav",
    language: str = "zh-CN",
    engine: str = "google",
    ctx: Context = None
) -> TranscriptionResult:
    """
    转写音频数据
    
    Args:
        audio_data: 音频数据字节
        format: 音频格式
        language: 语言代码
        engine: 识别引擎
        ctx: MCP 上下文
    """
    if ctx:
        await ctx.info("开始转写音频数据")
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
        temp_file.write(audio_data)
        temp_path = temp_file.name
    
    try:
        return await transcribe_audio_file(temp_path, language, engine, ctx)
    finally:
        # 清理临时文件
        os.unlink(temp_path)


@mcp.tool()
async def transcribe_with_remote_api(
    file_path: str,
    api_type: str = "bailian",  # 支持 bailian, openai, xunfei 等
    api_key: str = "",
    api_url: str = "",
    language: str = "zh-CN",
    ctx: Context = None
) -> TranscriptionResult:
    """
    通过远程API调用大模型进行语音转文字
    
    Args:
        file_path: 音频文件路径
        api_type: API类型 (bailian, openai, xunfei 等)
        api_key: API密钥
        api_url: API地址
        language: 语言代码
        ctx: MCP 上下文
    
    注意: 请在使用前配置自己的大模型API密钥和地址
    """
    if ctx:
        await ctx.info(f"通过远程API({api_type})转写音频: {file_path}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"音频文件不存在: {file_path}")
    
    # 获取API配置
    api_key = api_key or os.getenv(f"{api_type.upper()}_API_KEY")
    api_url = api_url or os.getenv(f"{api_type.upper()}_API_URL")
    
    if not api_key or not api_url:
        raise ValueError(f"请在参数或环境变量中配置{api_type}的API密钥和地址")
    
    if ctx:
        await ctx.report_progress(progress=0.3, total=1.0, message="正在调用远程API...")
    
    try:
        # 读取音频文件
        with open(file_path, "rb") as f:
            audio_data = f.read()
        
        # 根据API类型调用不同的接口
        if api_type == "bailian":
            result = await _call_bailian_api(audio_data, api_key, api_url, language, ctx)
        elif api_type == "openai":
            result = await _call_openai_api(audio_data, api_key, api_url, language, ctx)
        elif api_type == "xunfei":
            result = await _call_xunfei_api(audio_data, api_key, api_url, language, ctx)
        else:
            # 通用API调用
            result = await _call_generic_api(audio_data, api_key, api_url, language, ctx)
        
        if ctx:
            await ctx.report_progress(progress=0.9, total=1.0, message="正在处理结果...")
        
        # 获取音频信息
        audio_info = get_audio_info(file_path)
        
        return TranscriptionResult(
            text=result.get("text", ""),
            confidence=result.get("confidence", 1.0),
            language=language,
            duration=audio_info.duration,
            segments=result.get("segments", [])
        )
    except Exception as e:
        if ctx:
            await ctx.error(f"远程API调用失败: {str(e)}")
        raise


@mcp.tool()
async def batch_transcribe(
    file_paths: List[str],
    language: str = "zh-CN",
    engine: str = "google",
    ctx: Context = None
) -> List[TranscriptionResult]:
    """
    批量转写多个音频文件
    
    Args:
        file_paths: 音频文件路径列表
        language: 语言代码
        engine: 识别引擎
        ctx: MCP 上下文
    """
    if ctx:
        await ctx.info(f"开始批量转写 {len(file_paths)} 个文件")
    
    results = []
    for i, file_path in enumerate(file_paths):
        if ctx:
            progress = (i + 1) / len(file_paths)
            await ctx.report_progress(
                progress=progress,
                total=1.0,
                message=f"正在处理文件 {i+1}/{len(file_paths)}: {os.path.basename(file_path)}"
            )
        
        try:
            result = await transcribe_audio_file(file_path, language, engine, ctx)
            results.append(result)
        except Exception as e:
            if ctx:
                await ctx.error(f"转写文件 {file_path} 时出错: {str(e)}")
            # 添加错误结果
            results.append(TranscriptionResult(
                text="",
                confidence=0.0,
                language=language,
                duration=0.0,
                segments=[]
            ))
    
    return results


@mcp.tool()
async def get_supported_formats() -> SupportedFormats:
    """获取支持的音频格式和语言"""
    return SupportedFormats(
        input_formats=["wav", "mp3", "m4a", "flac", "ogg", "aac"],
        output_formats=["wav", "mp3", "txt", "srt", "vtt"],
        languages=["zh-CN", "en-US", "ja-JP", "ko-KR", "fr-FR", "de-DE", "es-ES", "ru-RU"]
    )


@mcp.tool()
async def analyze_audio_file(file_path: str) -> AudioInfo:
    """分析音频文件信息"""
    return get_audio_info(file_path)


@mcp.tool()
async def convert_audio_file_format(
    input_path: str,
    output_path: str,
    target_format: str = "wav",
    ctx: Context = None
) -> str:
    """
    转换音频文件格式
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        target_format: 目标格式
        ctx: MCP 上下文
    """
    if ctx:
        await ctx.info(f"正在转换音频格式: {input_path} -> {output_path}")
    
    try:
        result_path = convert_audio_format(input_path, output_path, target_format)
        if ctx:
            await ctx.info(f"格式转换完成: {result_path}")
        return result_path
    except Exception as e:
        if ctx:
            await ctx.error(f"格式转换失败: {str(e)}")
        raise


# 内部转写函数
async def _transcribe_with_remote_api(file_path: str, language: str, ctx: Context = None) -> TranscriptionResult:
    """使用远程API转写"""
    if ctx:
        await ctx.info("使用远程API转写，请确保已配置API密钥和地址")
    
    # 获取默认API配置
    api_type = os.getenv("DEFAULT_API_TYPE", "bailian")
    api_key = os.getenv(f"{api_type.upper()}_API_KEY")
    api_url = os.getenv(f"{api_type.upper()}_API_URL")
    
    if not api_key or not api_url:
        raise ValueError(f"请在环境变量中配置{api_type}的API密钥和地址")
    
    return await transcribe_with_remote_api(file_path, api_type, api_key, api_url, language, ctx)


async def _call_bailian_api(audio_data: bytes, api_key: str, api_url: str, language: str, ctx: Context = None) -> Dict[str, Any]:
    """调用阿里云百炼API"""
    if ctx:
        await ctx.report_progress(progress=0.5, total=1.0, message="正在调用阿里云百炼API...")
    
    try:
        # 将音频数据编码为base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # 构建请求数据
        payload = {
            "audio": audio_base64,
            "language": language,
            "format": "wav"  # 可根据实际音频格式调整
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 发送请求
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # 解析百炼API响应
        if "result" in result:
            return {
                "text": result["result"].get("text", ""),
                "confidence": result["result"].get("confidence", 1.0),
                "segments": result["result"].get("segments", [])
            }
        else:
            return {
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 1.0),
                "segments": result.get("segments", [])
            }
    except Exception as e:
        if ctx:
            await ctx.error(f"百炼API调用失败: {str(e)}")
        raise


async def _call_openai_api(audio_data: bytes, api_key: str, api_url: str, language: str, ctx: Context = None) -> Dict[str, Any]:
    """调用OpenAI Whisper API"""
    if ctx:
        await ctx.report_progress(progress=0.5, total=1.0, message="正在调用OpenAI Whisper API...")
    
    try:
        # 构建请求数据
        files = {
            "file": ("audio.wav", audio_data, "audio/wav")
        }
        
        data = {
            "model": "whisper-1",
            "language": language
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        # 发送请求
        response = requests.post(api_url, files=files, data=data, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        return {
            "text": result.get("text", ""),
            "confidence": 1.0,  # OpenAI不提供置信度
            "segments": []
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"OpenAI API调用失败: {str(e)}")
        raise


async def _call_xunfei_api(audio_data: bytes, api_key: str, api_url: str, language: str, ctx: Context = None) -> Dict[str, Any]:
    """调用讯飞API"""
    if ctx:
        await ctx.report_progress(progress=0.5, total=1.0, message="正在调用讯飞API...")
    
    try:
        # 将音频数据编码为base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # 构建请求数据
        payload = {
            "audio": audio_base64,
            "language": language,
            "format": "wav"
        }
        
        headers = {
            "X-Appid": api_key,
            "Content-Type": "application/json"
        }
        
        # 发送请求
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        return {
            "text": result.get("text", ""),
            "confidence": result.get("confidence", 1.0),
            "segments": result.get("segments", [])
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"讯飞API调用失败: {str(e)}")
        raise


async def _call_generic_api(audio_data: bytes, api_key: str, api_url: str, language: str, ctx: Context = None) -> Dict[str, Any]:
    """通用API调用"""
    if ctx:
        await ctx.report_progress(progress=0.5, total=1.0, message="正在调用通用API...")
    
    try:
        # 将音频数据编码为base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # 构建请求数据
        payload = {
            "audio": audio_base64,
            "language": language
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 发送请求
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        return {
            "text": result.get("text", ""),
            "confidence": result.get("confidence", 1.0),
            "segments": result.get("segments", [])
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"通用API调用失败: {str(e)}")
        raise


async def _transcribe_with_google(file_path: str, language: str, ctx: Context = None) -> TranscriptionResult:
    """使用 Google Speech Recognition 引擎转写"""
    if ctx:
        await ctx.report_progress(progress=0.3, total=1.0, message="正在初始化 Google Speech Recognition...")
    
    try:
        recognizer = sr.Recognizer()
        
        # 转换音频格式为 WAV
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            convert_audio_format(file_path, temp_path, "wav")
            
            if ctx:
                await ctx.report_progress(progress=0.6, total=1.0, message="正在转写音频...")
            
            # 读取音频文件
            with sr.AudioFile(temp_path) as source:
                audio = recognizer.record(source)
            
            # 转写
            text = recognizer.recognize_google(audio, language=language)
            
            if ctx:
                await ctx.report_progress(progress=0.9, total=1.0, message="正在处理结果...")
            
            # 获取音频信息
            audio_info = get_audio_info(file_path)
            
            return TranscriptionResult(
                text=text,
                confidence=1.0,  # Google 不提供置信度
                language=language,
                duration=audio_info.duration,
                segments=[]
            )
        finally:
            # 清理临时文件
            os.unlink(temp_path)
    except Exception as e:
        if ctx:
            await ctx.error(f"Google Speech Recognition 转写失败: {str(e)}")
        raise


async def _transcribe_with_sphinx(file_path: str, language: str, ctx: Context = None) -> TranscriptionResult:
    """使用 CMU Sphinx 引擎转写"""
    if ctx:
        await ctx.report_progress(progress=0.3, total=1.0, message="正在初始化 CMU Sphinx...")
    
    try:
        recognizer = sr.Recognizer()
        
        # 转换音频格式为 WAV
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            convert_audio_format(file_path, temp_path, "wav")
            
            if ctx:
                await ctx.report_progress(progress=0.6, total=1.0, message="正在转写音频...")
            
            # 读取音频文件
            with sr.AudioFile(temp_path) as source:
                audio = recognizer.record(source)
            
            # 转写
            text = recognizer.recognize_sphinx(audio, language=language)
            
            if ctx:
                await ctx.report_progress(progress=0.9, total=1.0, message="正在处理结果...")
            
            # 获取音频信息
            audio_info = get_audio_info(file_path)
            
            return TranscriptionResult(
                text=text,
                confidence=1.0,  # Sphinx 不提供置信度
                language=language,
                duration=audio_info.duration,
                segments=[]
            )
        finally:
            # 清理临时文件
            os.unlink(temp_path)
    except Exception as e:
        if ctx:
            await ctx.error(f"CMU Sphinx 转写失败: {str(e)}")
        raise


# 资源
@mcp.resource("audio://info/{file_path}")
def get_audio_file_info(file_path: str) -> str:
    """获取音频文件信息"""
    try:
        info = get_audio_info(file_path)
        return json.dumps(info.model_dump(), indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)


@mcp.resource("audio://formats")
def get_supported_audio_formats() -> str:
    """获取支持的音频格式"""
    formats = SupportedFormats(
        input_formats=["wav", "mp3", "m4a", "flac", "ogg", "aac"],
        output_formats=["wav", "mp3", "txt", "srt", "vtt"],
        languages=["zh-CN", "en-US", "ja-JP", "ko-KR", "fr-FR", "de-DE", "es-ES", "ru-RU"]
    )
    return json.dumps(formats.model_dump(), indent=2, ensure_ascii=False)


# 提示模板
@mcp.prompt(title="语音转文字助手")
def speech_to_text_assistant() -> str:
    """语音转文字助手提示模板"""
    return """
你是一个专业的语音转文字助手。我可以帮助你：

1. 转写音频文件为文字
2. 批量处理多个音频文件
3. 支持多种音频格式（WAV, MP3, M4A, FLAC, OGG, AAC）
4. 支持多种识别引擎（Google Speech Recognition, Whisper, CMU Sphinx）
5. 支持多种语言（中文、英文、日文、韩文等）

请告诉我你需要转写什么音频文件，或者有什么其他问题。
"""


@mcp.prompt(title="音频格式转换助手")
def audio_format_converter() -> str:
    """音频格式转换助手提示模板"""
    return """
我是音频格式转换助手。我可以帮助你：

1. 转换音频文件格式
2. 分析音频文件信息
3. 支持多种输入格式：WAV, MP3, M4A, FLAC, OGG, AAC
4. 支持多种输出格式：WAV, MP3

请告诉我你需要转换什么格式的音频文件。
"""



def main():
    """主入口函数"""
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("语音转文字 MCP 服务器")
        print("用法: dw-mcp-server")
        print("这是一个 MCP 服务器，支持多种音频格式的语音转文字功能")
        return
    
    # 运行 MCP 服务器
    asyncio.run(mcp.run())


if __name__ == "__main__":
    main()