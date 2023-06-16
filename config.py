#!/usr/bin/env python
# encoding=utf8
# Time    : 2022/4/22 11:16 上午
# Author  : xing tian wei
# File    : config.py

import streamlit as st


def turn_supplement(flag, flag_1, flag_2):
	supplement = ""
	
	if flag == 0:
		if flag_1 + flag_2 == 0:
			supplement = ''
		elif flag_1 + flag_2 == 2:
			supplement = '完成敏感词添加'
		elif flag_1 + flag_2 == 3:
			supplement = '完成敏感词移除'
		else:
			assert flag_1 + flag_2 == 5, 'flag_1 + flag_2 的结果有异常'
			supplement = '完成敏感词的添加、移除'
	elif flag == 1:
		if flag_1 + flag_2 == 0:
			supplement = '完成敏感词袋初始化'
		elif flag_1 + flag_2 == 2:
			supplement = '完成敏感词袋初始化、添加'
		elif flag_1 + flag_2 == 3:
			supplement = '完成敏感词袋初始化、移除'
		else:
			assert flag_1 + flag_2 == 5, 'flag_1 + flag_2 的结果有异常'
			supplement = '完成敏感词袋初始化、添加、移除'
	return supplement