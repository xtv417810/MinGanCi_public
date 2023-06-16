#!/usr/bin/env python
# encoding=utf8
# Time    : 2022/4/21 3:39 下午
# Author  : xing tian wei
# File    : data_processing.py

import os
from mysql_get import read_mysql
import streamlit as st
import logging
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# path_dir = ["m_无标签敏感词库", "m_无标签敏感词库2", "m_无标签敏感词库3"]
# save_file = 'data.txt'


def data_handle_init(path_dir, save_file):
	data = set()
	for path in path_dir:
		# 1情况
		if path == "m_无标签敏感词库":
			for file in os.listdir(path):
				file_path = path + '/' + file
				with open(file_path, 'r+', encoding='utf8', errors='ignore') as fr:
					res = fr.readlines()
					res = map(lambda x: x.strip(), res)  ###
					data = data | set(res)  # 集合相加，用｜
		# 2情况
		if path == "m_无标签敏感词库2":
			for file in os.listdir(path):
				file_path = path + '/' + file
				with open(file_path, 'r', encoding='utf8', errors='ignore')  as fr:
					res = fr.readlines()
					res = map(lambda x: x.strip().split('|')[0], res)  ###
					data = data | set(res)
		# 3情况
		if path == "m_无标签敏感词库3":
			for file in os.listdir(path):
				file_path = path + '/' + file
				with open(file_path, 'r', encoding='utf8', errors='ignore')  as fr:
					res = fr.readlines()
					res = map(lambda x: x.strip().split('=')[0], res)  ###
					data = data | set(res)
	
	data = set(_ for _ in data if _ != "")  # 去空
	# print(data)
	with open(save_file, 'w+') as fw:
		for dd in data:
			fw.writelines(dd + '\n')

def add_keywords_refresh(save_file_add, sensitive_word_ls):
	word_map = map(lambda x: x + '\n', sensitive_word_ls)
	word_set = set(word_map)
	tp_flag = open(save_file_add, 'r+', encoding='utf8', errors='ignore').readlines()
	with open(save_file_add, 'a+', encoding='utf8', errors='ignore') as fa:
		for ws in word_set:
			if ws not in tp_flag:
				fa.writelines(ws)

def remove_keywords_refresh(save_file_remove, sensitive_word_ls):
	word_map = map(lambda x: x + '\n', sensitive_word_ls)
	word_set = set(word_map)
	tp_flag = open(save_file_remove, 'r+', encoding='utf8', errors='ignore').readlines()
	for ws in word_set:
		if ws in tp_flag:
			tp_flag.remove(ws)
	with open(save_file_remove, 'w+', encoding='utf8', errors='ignore') as fw:
		fw.writelines(tp_flag)

def data_handle_init_4_mysql(df_sensitiveword, save_file):
	data = set(df_sensitiveword['word'])
	data = set(_ for _ in data if _ != '')
	with open(save_file, 'w+') as fw:
		for dd in data:
			fw.writelines(dd + '\n')

def keywords_bag_init_judge(use_path_dir_or_mysql, path_dir, save_file, init_bag_flag=''):
	
	if not os.path.exists(save_file):
		flag = 1
		if use_path_dir_or_mysql == 'path_dir':
			data_handle_init(path_dir, save_file)  # 产生一个save_file文件，已存在则覆盖
		elif use_path_dir_or_mysql == 'mysql':
			df_sensitiveword = read_mysql()
			""" 打印log日志 """
			# logger.info('读到了mysql敏感词')
			# logger.info(df_sensitiveword[0:5])
			data_handle_init_4_mysql(df_sensitiveword, save_file)  # 产生一个save_file文件，已存在则覆盖
	if init_bag_flag == 'init':
		flag = 1
		if use_path_dir_or_mysql == 'path_dir':
			data_handle_init(path_dir, save_file)  # 产生一个save_file文件，已存在则覆盖
		elif use_path_dir_or_mysql == 'mysql':
			df_sensitiveword = read_mysql()
			data_handle_init_4_mysql(df_sensitiveword, save_file)    # 产生一个save_file文件，已存在则覆盖
	else:
		flag = 0
	return flag
	

