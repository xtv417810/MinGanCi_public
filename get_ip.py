#!/usr/bin/env python
# encoding=utf8
# Time    : 2022/5/12 2:06 下午
# Author  : xing tian wei
# File    : get_ip.py

import logging
# 初始化
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 方法1
# import socket
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect(("8.8.8.8", 80))
# print(s.getsockname()[0])


# 方法2，最推荐，泛化能力最强
import socket
def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()

    return IP



if __name__ == '__main__':
    ip = extract_ip()
    print(ip)
    print(type(ip))
    logger.info(ip)
    logger.info(type(ip))
