# TYK计算器MCP服务器

一个基于MCP协议的简单计算器服务器，提供基本的数学运算功能。

## 功能特性

- 支持加法、减法、乘法和除法运算
- 基于MCP协议，可与LLM模型集成
- 提供资源接口展示支持的操作

## 安装

```bash
pip install tyk-calculator-mcp-server
```

## 使用方法

安装完成后，可以通过以下命令启动服务器：

```bash
run-tyk-calculator
```

或者直接运行Python模块：

```bash
python -m tyk_calculator_mcp_server
```

## 依赖项

- Python 3.8或更高版本
- mcp包

## 许可证

MIT License