"""命令行入口模块"""

import argparse
import sys
from .server import create_mcp_server


def main():
    """
    命令行主入口函数
    
    解析命令行参数并启动MCP服务器
    """
    parser = argparse.ArgumentParser(
        description="Word to Text MCP Server - Word文档转文本分析服务器"
    )
    
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="sse",
        help="传输协议类型 (默认: sse)"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="服务器主机地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=7264,
        help="服务器端口号 (默认: 7264)"
    )
    
    parser.add_argument(
        "--name",
        default="Document Analysis Server",
        help="服务器名称 (默认: Document Analysis Server)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    args = parser.parse_args()
    
    try:
        # 创建MCP服务器
        mcp = create_mcp_server(args.name)
        
        print(f"启动Word文档分析MCP服务器...")
        print(f"服务器名称: {args.name}")
        print(f"传输协议: {args.transport}")
        
        if args.transport == "stdio":
            print("使用标准输入输出模式")
            mcp.run()
        else:
            print(f"服务器地址: {args.host}:{args.port}")
            mcp.run(
                transport=args.transport,
                host=args.host,
                port=args.port
            )
            
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()