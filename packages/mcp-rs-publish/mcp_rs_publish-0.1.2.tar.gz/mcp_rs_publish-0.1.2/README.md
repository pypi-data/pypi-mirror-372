# 最简单的MCP服务器

这是一个基于Python实现的最简单的MCP（Model Context Protocol）服务器，提供了基础的工具函数。

## 功能特性

该MCP服务器包含以下工具：

### 1. echo - 消息回显
- **功能**: 回显输入的消息
- **参数**: `message` (字符串) - 要回显的消息
- **示例**: 输入 "Hello World" 会返回 "回显: Hello World"

### 2. calculate - 数学计算
- **功能**: 执行简单的数学表达式
- **参数**: `expression` (字符串) - 数学表达式
- **示例**: 输入 "2 + 3 * 4" 会返回 "计算结果: 2 + 3 * 4 = 14"

### 3. get_time - 获取时间
- **功能**: 获取当前系统时间
- **参数**: 无
- **示例**: 返回当前时间，如 "当前时间: 2024-01-15 14:30:25"

### 4. reverse_text - 文本反转
- **功能**: 反转输入的文本内容
- **参数**: `text` (字符串) - 要反转的文本
- **示例**: 输入 "Hello" 会返回 "反转结果: olleH"

## 安装和运行

### 环境要求
- Python 3.13+
- 已安装 `mcp[cli]` 包

### 运行方式

#### 方式1: 直接运行
```bash
python mcp_rs_publish/command.py
```

#### 方式2: 作为模块运行
```bash
python -m mcp_rs_publish.command
```

#### 方式3: 使用项目脚本
```bash
mcp_rs_publish
```

## 配置说明

在 `config.json` 文件中配置MCP服务器：

```json
{
  "mcpServers": {
    "simple-mcp-server": {
      "command": "python",
      "args": ["-m", "mcp_rs_publish.command"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## 技术架构

- **框架**: 使用 `mcp` Python库
- **通信**: 基于stdio的标准输入输出通信
- **异步**: 使用 `asyncio` 实现异步处理
- **日志**: 内置日志系统，便于调试

## 扩展开发

要添加新的工具，只需在 `SimpleMCPServer` 类的 `_setup_handlers` 方法中：

1. 在 `handle_list_tools` 中添加工具定义
2. 在 `handle_call_tool` 中添加工具实现逻辑

## 注意事项

- 数学计算功能使用 `eval()` 函数，请确保输入安全
- 服务器使用stdio通信，适合与支持MCP协议的客户端集成
- 所有工具调用都是异步的，支持并发处理

## 许可证

本项目采用MIT许可证。
