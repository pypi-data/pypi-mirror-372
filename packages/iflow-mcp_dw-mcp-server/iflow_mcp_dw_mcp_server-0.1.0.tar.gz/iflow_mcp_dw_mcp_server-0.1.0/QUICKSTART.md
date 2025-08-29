# 快速开始指南

## 🚀 5分钟快速启动

### 1. 安装依赖

```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
# 开发模式 (推荐用于测试)
python run.py --dev

# 或直接启动服务器
python run.py

# 或使用 uv
uv run python main.py
```

### 3. 在 Claude Desktop 中安装

```bash
# 安装到 Claude Desktop
python run.py --install

# 或使用 uv
uv run mcp install main.py
```

### 4. 测试功能

```bash
# 运行测试
python run.py --test

# 查看配置
python run.py --config

# 验证配置
python run.py --validate
```

## 📋 基本使用

### 转写音频文件

```python
# 使用默认设置转写
result = await transcribe_audio_file("/path/to/audio.wav")

# 指定语言和引擎
result = await transcribe_audio_file(
    file_path="/path/to/audio.mp3",
    language="zh-CN",
    engine="whisper"
)
```

### 批量转写

```python
# 批量转写多个文件
file_paths = [
    "/path/to/audio1.wav",
    "/path/to/audio2.mp3",
    "/path/to/audio3.m4a"
]

results = await batch_transcribe(
    file_paths=file_paths,
    language="zh-CN",
    engine="whisper"
)
```

### 分析音频文件

```python
# 获取音频文件信息
info = await analyze_audio_file("/path/to/audio.wav")
print(f"格式: {info.format}")
print(f"时长: {info.duration}秒")
print(f"采样率: {info.sample_rate}Hz")
```

## 🔧 配置选项

### 环境变量

复制 `env.example` 为 `.env` 并修改：

```bash
cp env.example .env
```

主要配置项：

```bash
# 默认语言
DEFAULT_LANGUAGE=zh-CN

# 默认引擎
DEFAULT_ENGINE=remote_api

# 默认API类型
DEFAULT_API_TYPE=bailian

# API配置
BAILIAN_API_KEY=your_bailian_api_key
BAILIAN_API_URL=https://bailian.aliyuncs.com/v1/audio/transcriptions

# 最大文件大小 (MB)
MAX_FILE_SIZE=100
```

### 命令行参数

```bash
# 指定主机和端口
python run.py --host 127.0.0.1 --port 8080

# 启用调试模式
python run.py --debug

# 开发模式
python run.py --dev
```

## 🎯 支持的格式

### 输入格式
- WAV, MP3, M4A, FLAC, OGG, AAC

### 识别引擎
- **远程API**: 阿里云百炼、OpenAI Whisper、讯飞等，准确率高，无需本地模型
- **Google Speech Recognition**: 在线，准确率高
- **CMU Sphinx**: 完全离线，轻量级

### 支持的语言
- 中文 (zh-CN)
- 英文 (en-US)
- 日文 (ja-JP)
- 韩文 (ko-KR)
- 法文 (fr-FR)
- 德文 (de-DE)
- 西班牙文 (es-ES)
- 俄文 (ru-RU)

## 🔍 故障排除

### 常见问题

1. **API密钥配置错误**
   ```bash
   # 检查环境变量
   echo $BAILIAN_API_KEY
   echo $BAILIAN_API_URL
   ```

2. **音频格式不支持**
   ```bash
   # 安装 ffmpeg
   # Windows: 下载 ffmpeg 并添加到 PATH
   # macOS: brew install ffmpeg
   # Linux: sudo apt install ffmpeg
   ```

3. **网络连接错误**
   - 检查网络连接
   - 检查API地址是否正确
   - 考虑使用本地引擎（Google Speech Recognition）

### 日志查看

```bash
# 查看日志文件
tail -f speech_to_text.log

# 启用详细日志
python run.py --debug
```

## 📚 更多信息

- [完整文档](README.md)
- [配置说明](config.py)
- [测试脚本](test_speech_to_text.py)

## 🆘 获取帮助

- 查看 `python run.py --help`
- 运行 `python run.py --test` 进行诊断
- 检查日志文件 `speech_to_text.log`

---

**提示**: 使用远程API需要配置API密钥和地址，请在使用前设置相应的环境变量或在调用时传入参数。 