#!/usr/bin/env python3
"""
语音转文字 MCP 服务器启动脚本
"""

import sys
import argparse
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import mcp
from config import get_config, validate_config


def setup_logging(debug: bool = False):
    """设置日志"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('speech_to_text.log', encoding='utf-8')
        ]
    )


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="语音转文字 MCP 服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run.py                    # 使用默认配置启动
  python run.py --host 127.0.0.1  # 指定主机
  python run.py --port 8080       # 指定端口
  python run.py --debug           # 启用调试模式
  python run.py --dev             # 开发模式
  python run.py --install         # 安装到 Claude Desktop
        """
    )
    
    parser.add_argument(
        '--host',
        default=None,
        help='服务器主机地址 (默认: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='服务器端口 (默认: 8000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--dev',
        action='store_true',
        help='开发模式 (使用 MCP 开发工具)'
    )
    
    parser.add_argument(
        '--install',
        action='store_true',
        help='安装到 Claude Desktop'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='显示当前配置'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='验证配置'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='运行测试'
    )
    
    return parser.parse_args()


def show_config():
    """显示当前配置"""
    config = get_config()
    import json
    print("当前配置:")
    print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))


def run_tests():
    """运行测试"""
    print("运行测试...")
    try:
        import test_speech_to_text
        asyncio.run(test_speech_to_text.main())
    except ImportError:
        print("❌ 测试文件不存在")
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def install_to_claude():
    """安装到 Claude Desktop"""
    print("安装到 Claude Desktop...")
    try:
        import subprocess
        result = subprocess.run(
            ["uv", "run", "mcp", "install", "main.py"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ 安装成功")
            print(result.stdout)
        else:
            print("❌ 安装失败")
            print(result.stderr)
    except Exception as e:
        print(f"❌ 安装失败: {e}")


def run_dev_mode():
    """运行开发模式"""
    print("启动开发模式...")
    try:
        import subprocess
        subprocess.run(["uv", "run", "mcp", "dev", "main.py"])
    except KeyboardInterrupt:
        print("\n开发模式已停止")
    except Exception as e:
        print(f"❌ 开发模式启动失败: {e}")


async def run_server(host: str, port: int, debug: bool):
    """运行服务器"""
    print(f"启动语音转文字 MCP 服务器...")
    print(f"主机: {host}")
    print(f"端口: {port}")
    print(f"调试模式: {'是' if debug else '否'}")
    print("-" * 50)
    
    try:
        import uvicorn
        uvicorn.run(
            mcp,
            host=host,
            port=port,
            log_level="debug" if debug else "info"
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    args = parse_arguments()
    
    # 设置日志
    setup_logging(args.debug)
    
    # 获取配置
    config = get_config()
    
    # 处理特殊命令
    if args.config:
        show_config()
        return
    
    if args.validate:
        if validate_config():
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
            sys.exit(1)
        return
    
    if args.test:
        run_tests()
        return
    
    if args.install:
        install_to_claude()
        return
    
    if args.dev:
        run_dev_mode()
        return
    
    # 更新配置
    if args.host:
        config.server.host = args.host
    if args.port:
        config.server.port = args.port
    if args.debug:
        config.server.debug = args.debug
    
    # 验证配置
    if not validate_config():
        print("❌ 配置验证失败")
        sys.exit(1)
    
    # 创建必要的目录
    temp_dir = Path(config.audio.temp_dir)
    temp_dir.mkdir(exist_ok=True)
    
    # 运行服务器
    asyncio.run(run_server(
        host=config.server.host,
        port=config.server.port,
        debug=config.server.debug
    ))


if __name__ == "__main__":
    main() 