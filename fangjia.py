#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import requests
import json
import xlwt

# https://bj.lianjia.com/fangjia/priceTrend/?region=city&region_id=110000&analysis=1 # 北京二手房供需走势
# https://bj.lianjia.com/fangjia/priceTrend/?region=city&region_id=110000 # 北京二手房价格走势

# 头部信息
headers = {
	'accept': '*/*',
	'accept-encoding': 'gzip, deflate, br',
	'accept-language': 'zh-CN,zh;q=0.9',
	'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
	'x-newrelic-id': 'UgcAVlBUGwQFU1NWAAUD',
	'x-requested-with': 'XMLHttpRequest'
}

def getPriceTrend(city, region, region_id, **kw):
	url = "https://{city}.lianjia.com/fangjia/priceTrend/?region={region}&region_id={region_id}".format(city=city, region=region, region_id=region_id)
	for item in kw.items():
		url = url + "&{key}={value}".format(key=item[0], value=item[1])
	response = requests.get(url, headers=headers)
	return response.status_code, response.text

def getHouseAnalysis(city, region, region_id):
	code, text = getPriceTrend(city, region, region_id, analysis=1)
	if code == 200:
		content = json.loads(text)
		return content.get('duration'), content.get('houseAmount'), content.get('customerAmount'), content.get('showAmount'), content.get('customerHouseRatio')

def getHousePriceTrend(city, region, region_id):
	code, text = getPriceTrend(city, region, region_id)
	if code == 200:
		content = json.loads(text)
		currentLevel = content.get('currentLevel')
		if currentLevel is None:
			return
		return currentLevel.get('month'), currentLevel.get('listPrice'), currentLevel.get('dealPrice')

# 在行添加标题
def addSheetRowTitle(sheet, title):
	for i in range(len(title)):
		sheet.write(0, i, title[i])

# 填写excel行
def addSheetRow(sheet, row_num, row_data):
	for i in range(len(row_data)):
		sheet.write(row_num, i, row_data[i])

# 填写excel列
def addSheetColumn(sheet, start_row, column_num, column_data):
	for i in range(len(column_data)):
		sheet.write(start_row+i, column_num, column_data[i])


def main():
	# 获取北京二手房供需走势数据
	duration, houseAmount, customerAmount, showAmount, customerHouseRatio = getHouseAnalysis('bj', 'city', 110000)
	# 创建一个excel对象
	book = xlwt.Workbook()
	sheet_analysis = book.add_sheet('北京二手房供需走势数据', cell_overwrite_ok=True)
	title = ['月份', '新增房源量', '新增客户量', '带看量', '客户量/房源量']
	addSheetRowTitle(sheet_analysis, title)
	addSheetColumn(sheet_analysis, 1, 0, duration)
	addSheetColumn(sheet_analysis, 1, 1, houseAmount)
	addSheetColumn(sheet_analysis, 1, 2, customerAmount)
	addSheetColumn(sheet_analysis, 1, 3, showAmount)
	addSheetColumn(sheet_analysis, 1, 4, customerHouseRatio)

	month, listPrice, dealPrice = getHousePriceTrend('bj', 'city', 110000)
	sheet_price = book.add_sheet('北京二手房价格走势数据', cell_overwrite_ok=True)
	addSheetRowTitle(sheet_price, ['月份', '全部-挂牌均价', '全部-参考均价', '一居-挂牌均价', '一居-参考均价', '二居-挂牌均价', '二居-参考均价', '三居-挂牌均价', '三居-参考均价', '其他-挂牌均价', '其他-参考均价'])
	addSheetColumn(sheet_price, 1, 0, month)
	addSheetColumn(sheet_price, 1, 1, listPrice.get('total'))
	addSheetColumn(sheet_price, 1, 2, dealPrice.get('total'))
	addSheetColumn(sheet_price, 1, 3, listPrice.get('1_bed'))
	addSheetColumn(sheet_price, 1, 4, dealPrice.get('1_bed'))
	addSheetColumn(sheet_price, 1, 5, listPrice.get('2_bed'))
	addSheetColumn(sheet_price, 1, 6, dealPrice.get('2_bed'))
	addSheetColumn(sheet_price, 1, 7, listPrice.get('3_bed'))
	addSheetColumn(sheet_price, 1, 8, dealPrice.get('3_bed'))
	addSheetColumn(sheet_price, 1, 9, listPrice.get('other'))
	addSheetColumn(sheet_price, 1, 10, dealPrice.get('other'))

	create_ouput_dir()

	book.save(get_output_dir() + '/fangjia.xls') # 保存excel
	print('成功保存北京二手房供需走势和房价走势数据')

def create_ouput_dir():
	output_path = get_output_dir()
	if not os.path.exists(output_path):
		os.makedirs(output_path)

def get_output_dir():
	return os.getcwd() + "/output"


if __name__ == '__main__':
	main()
