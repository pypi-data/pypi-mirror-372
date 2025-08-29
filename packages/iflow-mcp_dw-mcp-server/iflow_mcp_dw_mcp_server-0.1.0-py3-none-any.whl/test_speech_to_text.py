#!/usr/bin/env python3
"""
语音转文字 MCP 服务器测试脚本
"""

import asyncio
import tempfile
import os
from pathlib import Path

# 导入我们的 MCP 服务器
from main import mcp, transcribe_audio_file, analyze_audio_file, get_supported_formats


async def test_supported_formats():
    """测试获取支持的格式"""
    print("测试获取支持的格式...")
    try:
        formats = await get_supported_formats()
        print(f"支持的输入格式: {formats.input_formats}")
        print(f"支持的输出格式: {formats.output_formats}")
        print(f"支持的语言: {formats.languages}")
        print("✅ 格式测试通过")
    except Exception as e:
        print(f"❌ 格式测试失败: {e}")


async def test_audio_analysis():
    """测试音频文件分析"""
    print("\n测试音频文件分析...")
    
    # 创建一个测试音频文件（这里只是示例，实际需要真实的音频文件）
    test_audio_path = "test_audio.wav"
    
    if os.path.exists(test_audio_path):
        try:
            info = await analyze_audio_file(test_audio_path)
            print(f"音频格式: {info.format}")
            print(f"时长: {info.duration}秒")
            print(f"采样率: {info.sample_rate}Hz")
            print(f"声道数: {info.channels}")
            print(f"文件大小: {info.file_size}字节")
            print("✅ 音频分析测试通过")
        except Exception as e:
            print(f"❌ 音频分析测试失败: {e}")
    else:
        print("⚠️  跳过音频分析测试（需要测试音频文件）")


async def test_transcription():
    """测试语音转文字"""
    print("\n测试语音转文字...")
    
    # 这里需要一个真实的音频文件来测试
    test_audio_path = "test_audio.wav"
    
    if os.path.exists(test_audio_path):
        try:
            # 测试 Whisper 引擎
            print("测试 Whisper 引擎...")
            result = await transcribe_audio_file(
                file_path=test_audio_path,
                language="zh-CN",
                engine="whisper"
            )
            print(f"转写结果: {result.text}")
            print(f"置信度: {result.confidence}")
            print(f"语言: {result.language}")
            print(f"时长: {result.duration}秒")
            print("✅ Whisper 转写测试通过")
        except Exception as e:
            print(f"❌ Whisper 转写测试失败: {e}")
        
        try:
            # 测试 Google 引擎
            print("测试 Google Speech Recognition 引擎...")
            result = await transcribe_audio_file(
                file_path=test_audio_path,
                language="zh-CN",
                engine="google"
            )
            print(f"转写结果: {result.text}")
            print(f"置信度: {result.confidence}")
            print(f"语言: {result.language}")
            print(f"时长: {result.duration}秒")
            print("✅ Google 转写测试通过")
        except Exception as e:
            print(f"❌ Google 转写测试失败: {e}")
    else:
        print("⚠️  跳过转写测试（需要测试音频文件）")


async def test_mcp_server():
    """测试 MCP 服务器功能"""
    print("\n测试 MCP 服务器功能...")
    
    try:
        # 获取服务器信息
        server_info = mcp.get_server_info()
        print(f"服务器名称: {server_info.name}")
        print(f"服务器版本: {server_info.version}")
        print("✅ MCP 服务器测试通过")
    except Exception as e:
        print(f"❌ MCP 服务器测试失败: {e}")


async def create_test_audio():
    """创建测试音频文件"""
    print("\n创建测试音频文件...")
    
    try:
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        # 创建一个简单的测试音频文件
        # 生成一个 1 秒的 440Hz 正弦波
        audio = Sine(440).to_audio_segment(duration=1000)
        
        # 保存为 WAV 文件
        test_audio_path = "test_audio.wav"
        audio.export(test_audio_path, format="wav")
        
        print(f"✅ 测试音频文件已创建: {test_audio_path}")
        return test_audio_path
    except Exception as e:
        print(f"❌ 创建测试音频文件失败: {e}")
        return None


async def main():
    """主测试函数"""
    print("🚀 开始测试语音转文字 MCP 服务器")
    print("=" * 50)
    
    # 测试 MCP 服务器
    await test_mcp_server()
    
    # 测试支持的格式
    await test_supported_formats()
    
    # 创建测试音频文件
    test_audio_path = await create_test_audio()
    
    # 测试音频分析
    await test_audio_analysis()
    
    # 测试语音转文字
    await test_transcription()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    
    # 清理测试文件
    if test_audio_path and os.path.exists(test_audio_path):
        os.remove(test_audio_path)
        print(f"🧹 已清理测试文件: {test_audio_path}")


if __name__ == "__main__":
    asyncio.run(main()) 