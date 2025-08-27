# 计算器MCP服务器

一个提供简单加减乘除计算功能的MCP服务器。

## 功能特点

- 支持基本的四则运算：加、减、乘、除
- 提供MCP协议接口
- 包含详细的日志输出
- 简单易用的命令行接口

## 安装

```bash
pip install calculator-mcp-server
```

## 使用方法

安装完成后，可以通过以下命令启动服务器：

```bash
calculator-mcp-server
```

## 支持的操作

- `add(a, b)` - 计算两个数的和
- `subtract(a, b)` - 计算两个数的差
- `multiply(a, b)` - 计算两个数的积
- `divide(a, b)` - 计算两个数的商

## 依赖

- Python 3.7+ 
- mcp包