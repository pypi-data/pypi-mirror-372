# TYK Time Converter

一个将秒数转换为天、小时、分钟、秒格式的MCP服务。

## 功能

- 将输入的秒数转换为可读性更好的天、小时、分钟、秒格式
- 提供MCP服务接口，可以通过网络调用

## 安装

```bash
pip install tyk_time_converter
```

## 使用方法

```python
# 启动MCP服务器
python -m tyk_time_converter_server

# 然后可以通过MCP客户端调用convert_seconds_to_time工具
# 例如：输入4601秒，会返回 "1 小时 16 分钟 41 秒"
```

## 依赖

- mcp