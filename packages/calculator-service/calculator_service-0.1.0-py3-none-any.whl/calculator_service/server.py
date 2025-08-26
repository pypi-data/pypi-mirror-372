import math
from mcp.server.fastmcp.server import FastMCP

mcp = FastMCP("CalculatorService")

# 算术工具组
@mcp.tool()
def add(a: float, b: float) -> float:
    """执行浮点数加法运算"""
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """执行浮点数减法运算"""
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """执行浮点数乘法运算"""
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """执行浮点数除法运算
    Args:
        b: 除数（必须非零）
    """
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b


# 高级数学工具
@mcp.tool()
def power(base: float, exponent: float) -> float:
    """计算幂运算"""
    return base ** exponent

@mcp.tool()
def sqrt(number: float) -> float:
    """计算平方根"""
    return math.sqrt(number)

@mcp.tool()
def factorial(n: int) -> int:
    """计算整数阶乘"""
    return math.factorial(n)


def main():
    """命令行入口"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
