"""
Chat模块CLI入口
"""

import argparse
import logging
import sys
from pathlib import Path

from .server import create_chat_server
from .service import ChatService


def setup_logging(level: str = "INFO"):
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Chat服务")
    parser.add_argument("--port", type=int, default=8080, help="服务器端口")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--log-level", default="INFO", help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    
    try:
        # 创建并启动服务器
        server = create_chat_server(port=args.port)
        server.run(host=args.host, debug=args.debug)
        
    except KeyboardInterrupt:
        print("\\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"启动服务器失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()