"""MCP服务器主入口点 - 时间转换服务"""

import sys
import traceback
import datetime
# 确保安装了mcp包: pip install mcp
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("错误：需要安装 'mcp' 包才能运行此服务器。", file=sys.stderr)
    print("请运行: pip install mcp", file=sys.stderr)
    sys.exit(1)

# --- MCP服务器实现 ---
# 创建FastMCP服务器实例
mcp = FastMCP("时间转换服务器") # 服务器名称

# 定义一个工具 (Tool) - 转换秒数为天、小时、分钟、秒格式
@mcp.tool()
def convert_seconds_to_time(seconds: int) -> str:
    """将输入的秒数转换为天、小时、分钟、秒的格式

    参数:
        seconds: 要转换的秒数
    返回:
        格式化后的时间字符串，如 "1 天 2 小时 3 分钟 4 秒"
    """
    print(f"工具 'convert_seconds_to_time' 被调用，秒数: {seconds}", file=sys.stderr) # 增加日志
    
    # 计算天、小时、分钟、秒
    days = seconds // (24 * 3600)
    remaining_seconds = seconds % (24 * 3600)
    hours = remaining_seconds // 3600
    remaining_seconds %= 3600
    minutes = remaining_seconds // 60
    remaining_seconds %= 60
    
    # 构建结果字符串
    result_parts = []
    if days > 0:
        result_parts.append(f"{days} 天")
    if hours > 0:
        result_parts.append(f"{hours} 小时")
    if minutes > 0:
        result_parts.append(f"{minutes} 分钟")
    if remaining_seconds > 0 or not result_parts:  # 至少显示秒，除非输入为0
        result_parts.append(f"{remaining_seconds} 秒")
    
    return " ".join(result_parts)

# 定义另一个工具 - 获取当前时间
@mcp.tool()
def get_current_time() -> str:
    """获取当前系统的精确时间"""
    now = datetime.datetime.now()
    print(f"工具 'get_current_time' 被调用", file=sys.stderr) # 增加日志
    return f"当前时间是: {now.strftime('%Y-%m-%d %H:%M:%S.%f')}"

# 定义一个资源 (Resource)
@mcp.resource("time://current_iso")
def current_time_iso_resource() -> str:
    """提供ISO格式的当前时间资源"""
    now = datetime.datetime.now()
    print(f"资源 'time://current_iso' 被访问", file=sys.stderr) # 增加日志
    return now.isoformat()

# --- 服务器启动入口 ---
def main():
    """MCP服务器入口函数，供命令行或uvx调用"""
    try:
        print("时间转换MCP服务器正在启动...", file=sys.stderr)
        # 可以在这里添加更多的启动逻辑或检查
        print("MCP服务器实例已创建，准备运行...", file=sys.stderr)
        mcp.run() # 启动服务器，此函数会阻塞直到服务器停止
        print("时间转换MCP服务器已停止。", file=sys.stderr)
    except Exception as e:
        print(f"启动或运行时发生严重错误: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

# 允许直接通过 python -m time_converter_server 运行
if __name__ == "__main__":
    main()