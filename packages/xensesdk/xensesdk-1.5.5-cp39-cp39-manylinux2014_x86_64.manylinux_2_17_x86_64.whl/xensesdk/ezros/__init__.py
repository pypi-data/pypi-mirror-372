"""
EzROS - 基于 CycloneDDS 的 ROS2 风格通信框架

这是一个轻量级的通信框架，提供类似 ROS2 的接口：
- Node: 节点管理
- Topic: 话题发布/订阅
- Service: 服务请求/响应
- Logger: 日志系统

示例用法:
    import ezros
    
    # 初始化框架
    ezros.init()
    
    # 创建节点
    node = ezros.Node("my_node")
    
    # 创建发布者
    pub = node.create_publisher(ezros.StringMessage, "chatter")
    
    # 创建订阅者
    def callback(msg):
        print(f"收到消息: {msg.data}")
    sub = node.create_subscriber(ezros.StringMessage, "chatter", callback)
    
    # 运行节点
    ezros.spin(node)
"""

from .node import Node, Publisher, Subscriber, ServiceServer, ServiceClient, call_service
from .message import (
    Message, ServiceRequest, ServiceResponse,
    BytesMessage, StringMessage #, IntMessage, FloatMessage, BoolMessage
)
from .logger import Logger, get_logger, init_logging

from .context import (
    Rate, Timer, Context,
    init, shutdown, ok, spin, create_rate, wait_for_condition, setup_multi_net_interface
)

# 导入发布者监控工具
from .cli.publisher_monitor import (
    PublisherMonitor, monitor_publisher, unmonitor_publisher, get_global_monitor, get_topic_type, scan_node
)


# 版本信息
__version__ = "0.1.0"
__author__ = "Liu Jin"
__description__ = "基于 CycloneDDS 的 ROS2 风格通信框架"

# 导出的主要接口
__all__ = [
    # 核心类
    "Node", "Publisher", "Subscriber", "ServiceServer", "ServiceClient", "call_service",
    
    # 消息类型
    "Message", "ServiceRequest", "ServiceResponse",
    "BytesMessage", "StringMessage"
    
    # 日志
    "Logger", "get_logger", "init_logging",
    
    # 工具函数
    "Rate", "Timer", "Context",
    "init", "shutdown", "ok", "spin", "create_rate", "wait_for_condition", "setup_multi_net_interface"
    
    # 发布者监控工具
    "PublisherMonitor", "monitor_publisher", "unmonitor_publisher", "get_global_monitor", 
    "get_topic_type", "scan_node"

    
    # 版本信息
    "__version__", "__author__", "__description__"
]

from pathlib import Path
EZROS_DIR = Path(__file__).resolve().parent
CYCLONEDDS_CONFIG = EZROS_DIR / "CycloneDDS.xml"