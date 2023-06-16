#!/usr/bin/env python
# encoding=utf8
# Time    : 2022/5/10 2:44 下午
# Author  : xing tian wei
# File    : mysql_send.py

""" python模块库 """
import pymysql
from sqlalchemy import create_engine   # 创建数据库连接
import logging
import pandas as pd
import numpy as np


""" 自定义模块库 """
from get_ip import extract_ip



""" 初始化设置 """
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
chunk_size = 32
sensitiveword_path = './data.txt'

# MYSQL_URI = "mysql+pymysql://sanyu:InfoC0re@192.168.93.159:3306/zhengxie?charset=utf8"                  # 2个冒号的作用，user:password 和 ip:port。 至于/号后面的是逻辑库
# MYSQL_URI = "mysql+pymysql://root:abc123456@172.18.45.112:4306/new_sensitive_word?charset=utf8mb4"        # docker容器中mysql
MYSQL_URI = "mysql+pymysql://root:abc123456@10.1.8.58:4306/new_sensitive_word?charset=utf8mb4"          # docker容器中mysql
# MYSQL_URI = F"mysql+pymysql://root:abc123456@{extract_ip()}:4306/new_sensitive_word?charset=utf8mb4"    # 不建议，因为部署到容器运行时，会获取容器的网桥ip，造成ip不对。




def get_df_sensitive(sensitiveword_path):
    df_sensitive = pd.read_csv(sensitiveword_path, sep='\t', header=None)
    df_sensitive.columns = ['word']
    return df_sensitive


# 方法1，推荐
def storage_data_to_mysql(df_load):
    for g, df in df_load.groupby(np.arange(len(df_load)) // chunk_size):
        # db = pymysql.connect(host='192.168.93.159', port=3306, user='sanyu', password='InfoC0re', db='zhengxie', charset='utf8mb4')
        # db = pymysql.connect(host='172.18.45.112', port=4306, user='root', password='abc123456', db='new_sensitive_word', charset='utf8mb4')  # docker容器中mysql
        db = pymysql.connect(host='10.1.8.58', port=4306, user='root', password='abc123456', db='new_sensitive_word', charset='utf8mb4')     # docker容器中mysql
        # db = pymysql.connect(host=extract_ip(), port=4306, user='root', password='abc123456', db='new_sensitive_word', charset='utf8mb4')     # 不建议，因为部署到容器运行时，会获取容器的网桥ip，造成ip不对。

        try:
            update_list = [(item['word']) for _, item in df.iterrows()]
            with db.cursor() as cursor:
                ### 方法1
                sql = F""" INSERT IGNORE INTO `{'sensitive_word'}` (`word`) 
                            VALUE (%s)
                        """
                ### 方法2
                sql = "INSERT IGNORE INTO `{0}` (`word`)" \
                      "VALUE (%s)".format('sensitive_word')
                cursor.executemany(sql, update_list)
            db.commit()
        except Exception as e:
            logger.error(e)
            logger.error(df_load)
            logger.error(sql % update_list[0])
            raise Exception
        finally:
            db.close()

# 方法2
def storage_data_to_mysql_2(df_load):
    try:
        engine = create_engine(MYSQL_URI, encoding='utf-8', echo=False, pool_recycle=1800, pool_size=35)
        # df_load.to_sql(name='sensitive_word_2', con=engine, index=False, if_exists='append', chunksize=chunk_size)   # 1、name='sensitive_word_3' 表会在运行这行的时候自动创建（表名存在了会被删）。 2、if_exists='append'最好。 if_exists='replace'表示表中数据全删掉再重新导入。
        df_load.to_sql(name='sensitive_word_2', con=engine, index=False, if_exists='replace', chunksize=chunk_size)   # if_exists='append'最好。 if_exists='replace'表示表中数据全删掉再重新导入。
    except Exception as e:
        logger.error(e)
        raise Exception


if __name__ == '__main__':
    # 1、获取敏感词
    df_load = get_df_sensitive(sensitiveword_path)
    # df_load = pd.DataFrame()
    # df_load['word'] = ['xtv','xtv']
    logger.info(df_load[0:20])      # 查看前20条
    # 2、存储进mysql的sensitive_word表
    storage_data_to_mysql(df_load)
    # storage_data_to_mysql_2(df_load)
