#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup

# 头部信息
headers = {
	'accept': '*/*',
	'accept-encoding': 'gzip, deflate, br',
	'accept-language': 'zh-CN,zh;q=0.9',
	'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
	'x-newrelic-id': 'UgcAVlBUGwQFU1NWAAUD',
	'x-requested-with': 'XMLHttpRequest'
}

class Book(object):
	def get_book_name(self):
		pass

	def get_mulu(self):
		return []

	def get_chapter(self, index):
		pass

class BiqugeBook(Book):
	def __init__(self, name, id):
		self.name = name
		self.id = id

	def get_book_name(self):
		return self.name

	def get_mulu(self):
		mulu_url = 'https://www.biquge.cc/html/' + self.id
		response = requests.get(mulu_url)
		code, text = response.status_code, response.text
		if code == 200:
			soup = BeautifulSoup(text, "lxml")
			soup = soup.find('div', id = 'list').dl
			soup = soup.find_all('dt')[1]
			self.mulu = soup.find_next_siblings('dd')
			list = []
			for dd in self.mulu:
				list.append(dd.a.string)
			return list

	def get_chapter(self, index):
		chapter = self.mulu[index].a
		url = 'https://www.biquge.cc/html/' + self.id + '/' + chapter['href']
		print(url)
		response = requests.get(url)
		code, text = response.status_code, response.text
		if code == 200:
			soup = BeautifulSoup(text, "lxml")
			soup = soup.find('div', id = 'content')
			return soup.get_text()

class M555zwBook(Book):
	def __init__(self, name, id):
		self.name = name
		self.id = id

	def get_book_name(self):
		return self.name

	def get_mulu(self):
		mulu_url = 'https://m.555zw.com/book/' + self.id
		response = requests.get(mulu_url, headers = headers)
		response.encoding = 'gbk'
		code, text = response.status_code, response.text
		if code == 200:
			soup = BeautifulSoup(text, 'html.parser')
			soup = soup.find('section')
			mulu = soup.find_all('a')
			list = []
			self.mulu = []
			for a in mulu:
				self.mulu.insert(0, a)
				list.insert(0, a.get_text())
			return list

	def get_chapter(self, index):
		chapter = self.mulu[index]
		url = chapter['href']
		print(url)
		response = requests.get(url)
		response.encoding = 'gbk'
		code, text = response.status_code, response.text
		if code == 200:
			soup = BeautifulSoup(text, "html.parser")
			return soup.find('div', id = 'nr', class_ = 'nr_nr').get_text()

class BookTxtBook(Book):
	def __init__(self, name, id):
		self.name = name
		self.id = id

	def get_book_name(self):
		return self.name

	def get_mulu(self):
		mulu_url = 'https://www.booktxt.net/' + self.id
		response = requests.get(mulu_url, headers = headers)
		response.encoding = 'gbk'
		code, text = response.status_code, response.text
		if code == 200:
			soup = BeautifulSoup(text, 'html.parser')
			soup = soup.find('div', id = 'list')
			soup = soup.find_all('dt')[1]
			self.mulu = soup.find_next_siblings('dd')
			list = []
			for dd in self.mulu:
				list.append(dd.a.get_text())
			return list

	def get_chapter(self, index):
		chapter = self.mulu[index]
		url = 'https://www.booktxt.net/' + self.id + '/' + chapter.a['href']
		print(url)
		response = requests.get(url)
		response.encoding = 'gbk'
		code, text = response.status_code, response.text
		if code == 200:
			soup = BeautifulSoup(text, 'html.parser')
			return soup.find('div', id = 'content').get_text()

def show_mulu(mulu, start, end):
	print('================================')
	i = start
	while i <= end:
		desc = "%d: %s" % (i, mulu[i])
		print(desc)
		i = i + 1
	print('================================')

def read_book(book):
	mulu = book.get_mulu()
	start = 0
	end = len(mulu) - 1
	while True:
		show_mulu(mulu, start, end)
		index = input('请选择要阅读的章节索引:\n')
		if index == 'exit' or index == 'e' or index == 'quit' or index == 'q':
			break
		try:
			index = int(index)
			print(mulu[index] + ':')
			print(book.get_chapter(index))
			start = index - 5
			if start < 0:
				start = 0
			end = index + 5
			if end >= len(mulu):
				end = len(mulu) - 1
		except ValueError as e:
			break


def main():
	book_list = []
	# book_list.append(BiqugeBook('超陆权强国', '47/47097'))
	book_list.append(M555zwBook('超陆权强国', '32/32262'))
	book_list.append(BookTxtBook('史上最强崇祯', '8_8612'))
	print('================================')
	for i in range(len(book_list)):
		book = book_list[i]
		desc = "%d:\t%s" % (i, book.get_book_name())
		print(desc)
	print('================================')
	index = input('请选择阅读书籍索引，索引按顺序从0开始:\n')
	try:
		index = int(index)
		read_book(book_list[index])
	except ValueError as e:
		print('书籍索引输入错误，请输入有效的索引')

if __name__ == '__main__':
	main()