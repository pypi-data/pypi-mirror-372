"""MCP计算器服务器主入口点"""

import sys
import traceback
# 确保安装了mcp包: pip install mcp
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("错误：需要安装 'mcp' 包才能运行此服务器。", file=sys.stderr)
    print("请运行: pip install mcp", file=sys.stderr)
    sys.exit(1)

# --- MCP服务器实现 ---
# 创建FastMCP服务器实例
mcp = FastMCP("简单计算器服务器") # 服务器名称

# 定义加法计算工具
@mcp.tool()
def add(a: float, b: float) -> str:
    """计算两个数的和

    参数:
        a: 第一个数
        b: 第二个数
    """
    result = a + b
    print(f"工具 'add' 被调用: {a} + {b} = {result}", file=sys.stderr) # 增加日志
    return f"{a} + {b} = {result}"

# 定义减法计算工具
@mcp.tool()
def subtract(a: float, b: float) -> str:
    """计算两个数的差

    参数:
        a: 被减数
        b: 减数
    """
    result = a - b
    print(f"工具 'subtract' 被调用: {a} - {b} = {result}", file=sys.stderr) # 增加日志
    return f"{a} - {b} = {result}"

# 定义乘法计算工具
@mcp.tool()
def multiply(a: float, b: float) -> str:
    """计算两个数的积

    参数:
        a: 第一个数
        b: 第二个数
    """
    result = a * b
    print(f"工具 'multiply' 被调用: {a} * {b} = {result}", file=sys.stderr) # 增加日志
    return f"{a} * {b} = {result}"

# 定义除法计算工具
@mcp.tool()
def divide(a: float, b: float) -> str:
    """计算两个数的商

    参数:
        a: 被除数
        b: 除数（不能为0）
    """
    if b == 0:
        print(f"工具 'divide' 被调用，但除数为0: {a} / 0", file=sys.stderr) # 增加日志
        return "错误：除数不能为0"
    result = a / b
    print(f"工具 'divide' 被调用: {a} / {b} = {result}", file=sys.stderr) # 增加日志
    return f"{a} / {b} = {result}"

# 定义一个综合计算资源
@mcp.resource("calc://operations")
def calculator_operations_resource() -> str:
    """提供计算器支持的所有操作资源"""
    operations = "计算器支持的操作：\n1. add(a, b) - 加法计算\n2. subtract(a, b) - 减法计算\n3. multiply(a, b) - 乘法计算\n4. divide(a, b) - 除法计算"
    print(f"资源 'calc://operations' 被访问", file=sys.stderr) # 增加日志
    return operations

# --- 服务器启动入口 ---
def main():
    """MCP服务器入口函数，供命令行或uvx调用"""
    try:
        print("简单计算器MCP服务器正在启动...", file=sys.stderr)
        # 可以在这里添加更多的启动逻辑或检查
        print("MCP服务器实例已创建，准备运行...", file=sys.stderr)
        print("服务器支持的计算操作：add, subtract, multiply, divide", file=sys.stderr)
        mcp.run() # 启动服务器，此函数会阻塞直到服务器停止
        print("简单计算器MCP服务器已停止。", file=sys.stderr)
    except Exception as e:
        print(f"启动或运行时发生严重错误: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

# 允许直接通过 python calculator_mcp_server.py 运行
if __name__ == "__main__":
    main()