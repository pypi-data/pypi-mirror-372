from socket import *
import time
from datetime import datetime
import os
from .config import *

def read_address(file_path, default_address):
    """读取地址文件，如果文件不存在则使用默认地址"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf8') as f:
                address = f.read().strip()
                return address if address else default_address
        else:
            return default_address
    except Exception as e:
        print(f"读取地址文件时出错: {e}")
        return default_address

def guangbo(ip1=None, ip2=None):
    """
    广播消息发送函数
    参数:
        ip1: 第一个IP地址（可选，None表示使用文件中的地址）
        ip2: 第二个IP地址（可选，None表示使用文件中的地址）
    """
    # 优先级：用户输入参数 > 文件地址 > 默认地址
    address1 = ip1 if ip1 is not None else read_address(ADDRESS_FILE1, DEFAULT_IP1)
    address2 = ip2 if ip2 is not None else read_address(ADDRESS_FILE2, DEFAULT_IP2)
    
    # 创建地址列表
    addresses = [(address1, PORT), (address2, PORT)]
    
    # 创建socket
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    
    results = []
    
    # 循环向每个地址发送消息
    for address in addresses:
        try:
            s.sendto(MESSAGE, address)
            now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            result = f'{now} 向{address[0]}发送消息成功: 我正在运行'
            results.append(result)
            print(result)
        except Exception as e:
            now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            result = f'{now} 向{address[0]}发送消息失败，错误: {e}'
            results.append(result)
            print(result)
    
    s.close()
    
    nowtime = datetime.now()
    final_result = f'{nowtime} 所有消息发送完成!'
    results.append(final_result)
    print(final_result)
    
    return results

def get_current_addresses():
    """获取当前配置的地址（只读取，不更新）"""
    address1 = read_address(ADDRESS_FILE1, DEFAULT_IP1)
    address2 = read_address(ADDRESS_FILE2, DEFAULT_IP2)
    return address1, address2