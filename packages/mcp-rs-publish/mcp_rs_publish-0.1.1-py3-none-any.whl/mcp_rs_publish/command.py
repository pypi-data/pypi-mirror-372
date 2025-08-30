import asyncio
import logging
from mcp import Server, StdioServerParameters
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleMCPServer:
    """简单的MCP服务器类"""

    def __init__(self):
        self.server = Server("simple-mcp-server")
        self._setup_handlers()

    def _setup_handlers(self):
        """设置服务器处理器"""

        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """列出可用的工具"""
            tools = [
                Tool(
                    name="echo",
                    description="回显输入的消息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "要回显的消息"}
                        },
                        "required": ["message"],
                    },
                ),
                Tool(
                    name="calculate",
                    description="执行简单的数学计算",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "数学表达式，如 '2 + 3 * 4'",
                            }
                        },
                        "required": ["expression"],
                    },
                ),
                Tool(
                    name="get_time",
                    description="获取当前时间",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                Tool(
                    name="reverse_text",
                    description="反转文本内容",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "要反转的文本"}
                        },
                        "required": ["text"],
                    },
                ),
            ]
            return ListToolsResult(tools=tools)

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments) -> CallToolResult:
            """处理工具调用"""
            try:
                if name == "echo":
                    message = arguments.get("message", "")
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"回显: {message}")]
                    )

                elif name == "calculate":
                    expression = arguments.get("expression", "")
                    try:
                        # 安全地执行数学表达式
                        result = eval(expression, {"__builtins__": {}}, {})
                        return CallToolResult(
                            content=[
                                TextContent(
                                    type="text",
                                    text=f"计算结果: {expression} = {result}",
                                )
                            ]
                        )
                    except Exception as e:
                        return CallToolResult(
                            content=[
                                TextContent(type="text", text=f"计算错误: {str(e)}")
                            ]
                        )

                elif name == "get_time":
                    import datetime

                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    return CallToolResult(
                        content=[
                            TextContent(type="text", text=f"当前时间: {current_time}")
                        ]
                    )

                elif name == "reverse_text":
                    text = arguments.get("text", "")
                    reversed_text = text[::-1]
                    return CallToolResult(
                        content=[
                            TextContent(type="text", text=f"反转结果: {reversed_text}")
                        ]
                    )

                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"未知工具: {name}")]
                    )

            except Exception as e:
                logger.error(f"工具调用错误: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"工具执行错误: {str(e)}")]
                )


async def main():
    """主函数"""
    try:
        # 创建服务器实例
        server = SimpleMCPServer()

        # 启动服务器
        params = StdioServerParameters()
        async with server.server.run_stdio(params) as stream:
            logger.info("MCP服务器已启动")
            await stream.wait_closed()

    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        raise


if __name__ == "__main__":
    # 运行服务器
    asyncio.run(main())
