"""
广播消息发送模块 - guangbo
使用方式: 
  import guangbo
  guangbo.guangbo()  # 使用文件中的地址
  或
  guangbo.guangbo("192.168.1.100")  # 指定第一个地址，第二个使用文件中的地址
  或
  guangbo.guangbo("192.168.1.100", "192.168.1.101")  # 指定两个地址
"""

from .core import guangbo, get_current_addresses

__version__ = "0.1.0"
__author__ = "pengmin"
__all__ = ['guangbo', 'get_current_addresses']