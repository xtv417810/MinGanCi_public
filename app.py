#!/usr/bin/env python
# encoding=utf8
# Time    : 2022/4/18 4:36 下午
# Author  : xing tian wei
# File    : app.py



# python库
import streamlit as st
import logging
import time
import os

# 自定义函数
from run_word_filter import DFAFilter
from data_processing import keywords_bag_init_judge
from data_processing import add_keywords_refresh
from data_processing import remove_keywords_refresh
from config import turn_supplement

# 初始化
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# time.sleep(3)

# 初始化 flag 和 supplement 和 敏感词库
flag = 0
flag_1 = 0
flag_2 = 0
use_path_dir_or_mysql = 'path_dir'   #  'path_dir'表示从path_dir加载词库，'mysql'表示从mysql数据库表加载词库
path_dir = ["m_无标签敏感词库", "m_无标签敏感词库2", "m_无标签敏感词库3"]
save_file = 'data.txt'


# 初始化模型
gfw = DFAFilter()



""" 1,入参 """
init_bag_flag = st.sidebar.text_input('初始化敏感词袋(选填,填"init"表示走初始化)')
sensitive_word_add = st.sidebar.text_input('自定义添加敏感词(选填,添加多个敏感词时请以中文逗号分隔)')     # st.sidebar即 侧边栏显示功能
sensitive_word_remove = st.sidebar.text_input('自定义移除敏感词(选填,移除多个敏感词时请以中文逗号分隔)')
text = st.text_input('text')



""" 2,中间过程 """
try:
	
	# 加载词库
	flag = keywords_bag_init_judge(use_path_dir_or_mysql, path_dir, save_file, init_bag_flag)  # 调用
	gfw.parse(save_file)  # 词库   调用
	
	if sensitive_word_add != "" :   # 如果非空，则走 逗号分割 + 批量添加敏感词
		sensitive_word_ls = sensitive_word_add.split('，')  # 注：是中文逗号
		gfw.add_batch(sensitive_word_ls)                               # 调用
		flag_1 = 2
		add_keywords_refresh(save_file, sensitive_word_ls)             # 调用
	
	if sensitive_word_remove != "" :
		sensitive_word_ls = sensitive_word_remove.split('，')
		gfw.remove_refresh_batch(sensitive_word_ls)                    # 调用
		flag_2 = 3
		remove_keywords_refresh(save_file, sensitive_word_ls)          # 调用
	
	assert flag == 0 or flag ==1, "flag值返回错误"
	supplement = turn_supplement(flag, flag_1, flag_2)                 # 调用


	if text == "":
		code = 0
		message = '输入为空'
	else:
		code = 200
		message = '成功'
		
	# data = gfw.word_replace(text)
	# result = {"code": code, "message": message, "supplement":supplement, "result": data}
	data= gfw.word_replace_renew(text)
	result = {"code": code, "message": message, "supplement":supplement, "result": data[0], "idx": data[1]}

except Exception as e:
	logger.error(e)
	code = -1
	message = 'error'
	supplement = 'error'
	data = 'error'
	result = {"code": code, "message": message, "supplement": supplement, "result": data}


""" 3,出参 """
st.write(result)
