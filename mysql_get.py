#!/usr/bin/env python
# encoding=utf8
# Time    : 2022/5/11 3:41 下午
# Author  : xing tian wei
# File    : mysql_get.py

""" python模块库 """
import pymysql
import pandas as pd
from sqlalchemy import create_engine   # 创建数据库连接
from sqlalchemy.orm import sessionmaker


""" 自定义模块库 """
from get_ip import extract_ip

""" 初始化 """
# MYSQL_URI = "mysql+pymysql://sanyu:InfoC0re@192.168.93.159:3306/zhengxie?charset=utf8"                  # 2个冒号的作用，user:password 和 ip:port。 至于/号后面的是逻辑库
# MYSQL_URI = "mysql+pymysql://root:abc123456@172.18.45.112:4306/new_sensitive_word?charset=utf8mb4"        # docker容器中mysql
MYSQL_URI = "mysql+pymysql://root:abc123456@10.1.8.58:4306/new_sensitive_word?charset=utf8mb4"          # docker容器中mysql
# MYSQL_URI = F"mysql+pymysql://root:abc123456@{extract_ip()}:4306/new_sensitive_word?charset=utf8mb4"    # 不建议，因为部署到容器运行时，会获取容器的网桥ip，造成ip不对。


# 方法1、简单
def read_mysql():
    # db = pymysql.connect(host='192.168.93.159', port=3306, user='sanyu', passwd='InfoC0re', db='zhengxie', charset='utf8')
    # db = pymysql.connect(host='172.18.45.112', port=4306, user='root', password='abc123456', db='new_sensitive_word', charset='utf8mb4')    # docker容器中mysql
    db = pymysql.connect(host='10.1.8.58', port=4306, user='root', password='abc123456', db='new_sensitive_word', charset='utf8mb4')      # docker容器中mysql
    # db = pymysql.connect(host=extract_ip(), port=4306, user='root', password='abc123456', db='new_sensitive_word', charset='utf8mb4')     # 不建议，因为部署到容器运行时，会获取容器的网桥ip，造成ip不对。

    cursor = db.cursor(pymysql.cursors.DictCursor)  # 本来cursor.fetchall()返回[(),(),()]。但这里设置后将返回 [{},{},{}]。
    sql = """select * from sensitive_word
    """
    cursor.execute(sql)
    results = cursor.fetchall()    # [{},{},{}]
    db.close()
    res_dataframe = pd.DataFrame(results)
    # return res_dataframe[0:50]
    return res_dataframe


# 方法2、简单又快，推荐
def read_mysql_2():
    engine = create_engine(MYSQL_URI, encoding='utf-8', echo=False, pool_recycle=1800, pool_size=35)

    sql = """select * from sensitive_word
    """
    res_dataframe = pd.read_sql(sql=sql, con=engine)
    return res_dataframe


# 方法3、一般
def read_mysql_3():
    engine = create_engine(MYSQL_URI, encoding='utf-8', echo=False, pool_recycle=1800, pool_size=35)
    session = sessionmaker(bind=engine, autocommit=False)
    sn = session()

    sql = """select * from sensitive_word
    """
    res_dataframe = pd.read_sql(sql=sql, con=sn.bind)     # 因为bind=engine，所以sn.bind就是engine。
    sn.close()  #可以去掉
    return res_dataframe


# 方法4、一般
def read_mysql_4():
    engine = create_engine(MYSQL_URI, encoding='utf-8', echo=False, pool_recycle=1800, pool_size=35)
    session = sessionmaker(bind=engine, autocommit=False)
    sn = session()

    sql = """select * from sensitive_word
    """
    cursor = sn.execute(sql)
    res_list = cursor.fetchall()   # 返回list: [(),(),()]
    sn.close()  #可以去掉
    res_dic = [{'word':_[0], 'insert_time':_[1], 'update_time':_[2]} for _ in res_list]  # 核心，转换成dict
    res_dataframe = pd.DataFrame(res_dic)
    return res_dataframe


if __name__ == '__main__':
    # res = read_mysql()
    res = read_mysql()
    print(res[0:20])
