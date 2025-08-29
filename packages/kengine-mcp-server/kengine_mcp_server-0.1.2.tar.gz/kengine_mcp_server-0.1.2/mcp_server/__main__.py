"""
基于Python的kengine_mcp_server服务器主入口
实现MCP协议接口，通过标准输入/输出与AI客户端通信
"""

import json
import logging
import sys
import time
from typing import Dict, Any, Optional

# 导入kengine配置包
from kengine.config.logging_config import setup_logging
# 导入请求处理模块
from mcp_server.handlers import REQUEST_HANDLERS

# --------------------------
# 1. 常量定义
# --------------------------
# 服务器名称：确保所有地方使用相同的名称
SERVER_NAME = "kengine_mcp_server"

# --------------------------
# 2. 配置日志（避免干扰 stdio 协议）
# --------------------------
# 使用kengine.config.logging_config包中的setup_logging
setup_logging()
# 获取logger
logger = logging.getLogger(SERVER_NAME)

# --------------------------
# 3. MCP 协议常量
# --------------------------
# 支持的 MCP 请求类型
SUPPORTED_REQUEST_TYPES = {
    "initialize": "初始化连接",
    "heartbeat": "处理心跳检测",
    "version": "查询 kengine_mcp_server 版本",
    "tools/list": "获取可用工具列表",
    "tools/call": "调用工具"
}

# --------------------------
# 4. kengine_mcp_server 核心类
# --------------------------
class MCPServer:
    def __init__(self):
        self.running = True
        logger.info("kengine_mcp_server 初始化完成，等待客户端请求...")

    def parse_request(self, input_line: str) -> Optional[Dict[str, Any]]:
        """解析 stdin 中的 JSON 请求，支持JSON-RPC 2.0格式"""
        try:
            # 去除换行符和空白字符
            clean_input = input_line.strip()
            if not clean_input:
                return None
                
            # 解析 JSON
            request = json.loads(clean_input)
            
            # 检查是否是JSON-RPC 2.0请求
            if "jsonrpc" in request and request["jsonrpc"] == "2.0":
                # 转换为我们的请求格式
                request_id = request.get("id")
                # 确保id不为null，如果没有id则生成一个
                if request_id is None:
                    request_id = str(int(time.time() * 1000))  # 使用时间戳作为默认id
                
                converted_request = {
                    "type": request.get("method"),
                    "params": request.get("params", {}),
                    "id": request_id,
                    "jsonrpc": "2.0"
                }
                logger.debug(f"收到JSON-RPC 2.0请求: {json.dumps(converted_request, ensure_ascii=False)}")
                return converted_request
            else:
                # 兼容旧格式请求
                logger.debug(f"收到非JSON-RPC请求: {json.dumps(request, ensure_ascii=False)}")
                return request
                
        except json.JSONDecodeError as e:
            logger.error(f"解析请求失败（非 JSON 格式）: {input_line[:100]}... 错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"解析请求异常: {str(e)}", exc_info=True)
            return None

    # 删除 build_response 方法，因为现在每个处理函数都直接返回符合 JSON-RPC 2.0 规范的响应
    
    def handle_request(self, request_data: Dict[str, Any]) -> str:
        """处理请求并返回响应"""
        # 提取请求类型和ID
        request_type = request_data.get("type")
        request_id = request_data.get("id")
        
        # 记录请求开始时间（用于计算处理时间）
        start_time = time.time()
        logger.info(f"开始处理请求: {request_type}, ID: {request_id}")
        
        # 检查请求类型是否存在
        if not request_type:
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32600,
                    "message": f"请求缺少 'type' 字段（支持类型：{', '.join(SUPPORTED_REQUEST_TYPES.keys())}）"
                }
            }
            return json.dumps(error_response, ensure_ascii=False)

        try:
            # 根据请求类型获取对应的处理函数
            handler = REQUEST_HANDLERS.get(request_type)
            
            # 如果找到处理函数，则执行它
            if handler:
                return handler(request_id, request_data)
            
            # 如果没有找到处理函数，返回错误响应
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"不支持的请求类型: {request_type}（支持类型：{', '.join(SUPPORTED_REQUEST_TYPES.keys())}）"
                }
            }
            return json.dumps(error_response, ensure_ascii=False)
            
        except Exception as e:
            # 处理异常情况
            logger.error(f"处理 {request_type} 请求异常", exc_info=True)
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"处理请求失败: {str(e)}"
                }
            }
            return json.dumps(error_response, ensure_ascii=False)

    def run(self):
        """启动 MCP Server：监听 stdin 输入"""
        logger.info("kengine_mcp_server 已启动，开始监听请求（按 Ctrl+C 停止）")
        try:
            # 持续读取 stdin（客户端通过 stdin 发送请求）
            while self.running:
                # 读取一行输入（阻塞直到有输入）
                logger.debug("等待客户端请求...")
                input_line = sys.stdin.readline()
                if not input_line:
                    # stdin 关闭（客户端断开连接）
                    logger.warning("stdin 已关闭，客户端断开连接")
                    self.running = False
                    break

                # 记录请求开始时间
                request_start_time = time.time()
                
                # 解析并处理请求
                request_data = self.parse_request(input_line)
                if not request_data:
                    # 解析失败：返回错误响应
                    logger.error("请求解析失败（非 JSON 格式）")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,  # 解析失败时无法获取请求ID，传递null
                        "error": {
                            "code": -32700,  # JSON-RPC 2.0规范中的解析错误码
                            "message": "请求解析失败（非 JSON 格式）"
                        }
                    }
                    print(json.dumps(error_response, ensure_ascii=False), flush=True)  # 输出到 stdout（客户端读取）
                    continue

                # 处理请求并生成响应
                request_type = request_data.get("type", "unknown")
                request_id = request_data.get("id", "unknown")
                logger.info(f"开始处理请求: 类型={request_type}, ID={request_id}")
                
                response = self.handle_request(request_data)
                
                # 计算处理时间
                request_end_time = time.time()
                processing_time = request_end_time - request_start_time
                logger.info(f"请求处理完成: 类型={request_type}, ID={request_id}, 耗时={processing_time:.3f}秒")
                
                # 输出响应到 stdout（必须 flush，避免缓冲区阻塞）
                print(response, flush=True)

        except KeyboardInterrupt:
            logger.info("收到 Ctrl+C 信号，停止 kengine_mcp_server")
            self.running = False
        except Exception as e:
            logger.error("kengine_mcp_server 运行异常", exc_info=True)
            self.running = False
        finally:
            logger.info("kengine_mcp_server 已停止")

# --------------------------
# 5. 启动 kengine_mcp_server
# --------------------------
def main():
    """主函数"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="基于Python的kengine_mcp_server服务器")
    parser.add_argument("--verbose", action="store_true", help="启用详细日志")
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("已启用详细日志模式")
    
    try:
        # 创建并运行服务器
        server = MCPServer()
        server.run()
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号，正在退出kengine_mcp_server...")
    except Exception as e:
        logger.error(f"kengine_mcp_server 运行出错: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())