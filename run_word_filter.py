# !/usr/bin/env python
# encoding=utf8
# Time    : 2022/4/14 3:59 下午
# Author  : xing tian wei
# File    : run_word_filter.py
"""
@desc    : 敏感词过滤
"""

# 1
from collections import defaultdict
import re
import streamlit as st

# 2
from data_processing import data_handle_init

# 3
path_dir = ["m_无标签敏感词库", "m_无标签敏感词库2", "m_无标签敏感词库3"]
save_file = 'data.txt'
WordFilePath = './keywords.txt'

class NaiveFilter():
	'''Filter Messages from keywords

	very simple filter implementation

	# >>> f = NaiveFilter()
	# >>> f.add("sexy")
	# >>> f.filter("hello sexy baby")
	hello **** baby
	'''
	
	def __init__(self):
		self.keywords = set([])
	
	def parse(self, path):
		for keyword in open(path):
			self.keywords.add(keyword.strip().lower())
	
	def word_replace(self, message, repl="*"):
		message = str(message).lower()
		for kw in self.keywords:
			message = message.replace(kw, repl)
		return message

class BSFilter:
	'''Filter Messages from keywords

	Use Back Sorted Mapping to reduce replacement times

	# >>> f = BSFilter()
	# >>> f.add("sexy")
	# >>> f.filter("hello sexy baby")
	hello **** baby
	'''
	
	def __init__(self):
		self.keywords = []
		self.kwsets = set([])
		self.bsdict = defaultdict(set)
		self.pat_en = re.compile(r'^[0-9a-zA-Z]+$')  # english phrase or not
	
	def add(self, keyword):
		if isinstance(keyword, bytes):  # 等价于 if not isinstance(keyword, str):  （1）发现多个not （2）bytes是字节串，str是字符串
			keyword = keyword.decode('utf-8')
		keyword = keyword.lower()
		if keyword not in self.kwsets:
			self.keywords.append(keyword)
			self.kwsets.add(keyword)
			index = len(self.keywords) - 1
			for word in keyword.split():
				if self.pat_en.search(word):
					self.bsdict[word].add(index)
				else:
					for char in word:
						self.bsdict[char].add(index)
	
	def parse(self, path):
		with open(path, "r", encoding='utf-8') as f:
			for keyword in f:
				self.add(keyword.strip())
	
	def word_replace(self, message, repl="*"):
		if isinstance(message, bytes):  # 等价于 if not isinstance(message, str):  （1）发现多个not （2）bytes是字节串，str是字符串
			message = message.decode('utf-8')
		message = message.lower()
		for word in message.split():
			if self.pat_en.search(word):
				for index in self.bsdict[word]:
					message = message.replace(self.keywords[index], repl)
			else:
				for char in word:
					for index in self.bsdict[char]:
						message = message.replace(self.keywords[index], repl)
		return message


class DFAFilter():  # DFA算法，也称确定有穷自动机
	'''Filter Messages from keywords

	Use DFA to keep algorithm perform constantly

	# >>> f = DFAFilter()
	# >>> f.add("sexy")
	# >>> f.filter("hello sexy baby")
	hello **** baby
	'''

	def __init__(self):
		self.keyword_chains = {}
		self.keyword_add_remove_set = set()     # 自添1
		self.delimit = '\x00'

	def add(self, keyword):
		if isinstance(keyword, bytes):  # 等价于 if not isinstance(keyword, str):  （1）发现多个not （2）bytes是字节串，str是字符串
			keyword = keyword.decode('utf-8')
		keyword = keyword.lower()
		chars = keyword.strip()
		self.add_pond(chars)
		if not chars:
			return None
		level = self.keyword_chains
		for i in range(len(chars)):
			if chars[i] in level:
				level = level[chars[i]]
			else:
				if not isinstance(level, dict):
					break
				for j in range(i, len(chars)):
					level[chars[j]] = {}
					last_level, last_char = level, chars[j]
					level = level[chars[j]]
				last_level[last_char] = {self.delimit: 0}
				break
		if i == len(chars) - 1:
			level[self.delimit] = 0

	def add_batch(self, keyword_list):  # 自添2
		for keyword in keyword_list:
			self.add(keyword)

	def add_pond(self, keyword):        # 自添3
		self.keyword_add_remove_set.add(keyword)

	def remove_pond(self, keyword):     # 自添4
		if isinstance(keyword, bytes):  # 等价于 if not isinstance(keyword, str):  （1）发现多个not （2）bytes是字节串，str是字符串
			keyword = keyword.decode('utf-8')
		keyword = keyword.lower()
		chars = keyword.strip()
		if chars in self.keyword_add_remove_set:
			self.keyword_add_remove_set.remove(chars)

	def remove_mini(self):      # 自添5
		for word in self.keyword_add_remove_set:
			self.add(word)

	def remove_refresh(self, keyword):   # 自添6
		self.keyword_chains = {}         # 核心， 重置
		self.remove_pond(keyword)        # 核心， 更新 self.keyword_add_remove_set
		self.remove_mini()

	def remove_refresh_batch(self, keyword_list):   # 自添7
		self.keyword_chains = {}                    # 核心， 重置
		for keyword in keyword_list:
			self.remove_pond(keyword)               # 核心， 更新 self.keyword_add_remove_set
		self.remove_mini()

	def parse(self, path):
		with open(path, encoding='utf-8') as f:
			for keyword in f:
				self.add(keyword.strip())

	def word_replace(self, message, repl="*"):
		if isinstance(message, bytes):  # 等价于 if not isinstance(keyword, str):  （1）发现多个not （2）bytes是字节串，str是字符串
			message = message.decode('utf-8')
		message = message.lower()
		ret = []
		start = 0
		while start < len(message):
			level = self.keyword_chains
			step_ins = 0
			for char in message[start:]:
				if char in level:
					step_ins += 1
					if self.delimit not in level[char]:
						level = level[char]
					else:
						ret.append(repl * step_ins)
						start += step_ins - 1
						break
				else:
					ret.append(message[start])
					break
			else:
				ret.append(message[start])
			start += 1
		
		return ''.join(ret)
	
	"""
		更新的地方就是添加了return_idx = True
		如果
	"""
	def word_replace_renew(self, message, repl="*", return_idx = True):
		if isinstance(message, bytes):  # 等价于 if not isinstance(keyword, str):  （1）发现多个not （2）bytes是字节串，str是字符串
			message = message.decode('utf-8')
		message = message.lower()
		ret = []
		start = 0
		
		if return_idx == True:
			idx_list = []      # 自添8，索引
		else:
			pass
		
		while start < len(message):
			level = self.keyword_chains
			step_ins = 0
			for char in message[start:]:
				if char in level:
					step_ins += 1
					if self.delimit not in level[char]:
						level = level[char]
					else:
						if return_idx == True:
							res_len = len(''.join(ret))  # 自添9，索引
							idx_list.append(F"{res_len}:{res_len+step_ins-1}")   # 自添10
						else:
							pass
						ret.append(repl * step_ins)
						start += step_ins - 1
						break
				else:
					ret.append(message[start])
					break
			else:
				ret.append(message[start])
			start += 1
		
		# 返回结果
		if return_idx == True:
			return ''.join(ret), idx_list   # 2个返回
		else:
			return ''.join(ret)


if __name__ == '__main__':
	""" 1，load 数据 """
	data_handle_init(path_dir=path_dir,save_file=save_file)
	
	""" 2，模型实例化 """
	# gfw = NaiveFilter()   # 方法1
	# gfw = BSFilter()    # 方法2
	gfw = DFAFilter()  # 方法3   推荐
	
	# 初始化词库
	gfw.parse(WordFilePath)  # 词库1
	gfw.parse(save_file)     # 词库2, 叠加了
	gfw.add('邓小平')       	 # 手动添加一个敏感词可使用 .add()
	gfw.add('Con-man')
	gfw.add('Con merchant')
	gfw.add('KD')
	gfw.add_batch(['新新','luyumine'])   # 批量添加敏感词
	
	gfw.remove_refresh('邓小平')
	gfw.remove_refresh_batch(['KD','新新'])

	
	""" 3，测试 """
	content = "yes，邓小平，kd，方法，习近平，李克强，中央，Con-man，大奶子，Con merchant, 提供神奇蘑菇, 新新， luyumine"
	# result = gfw.word_replace(content)
	# print(result)
	result = gfw.word_replace_renew(content)
	print(result)
	