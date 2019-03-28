#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import re
import xlwt
import time
import threading

# 要抓取的目标网页地址
# https://www.etf.com/etf-finder-funds-api//-aum/0/20/1
# https://www.etf.com/etf-finder-funds-api//-aum/20/20/1
# https://www.etf.com/etf-finder-funds-api//-aum/40/20/1

# 头部信息
headers = {
	'accept': '*/*',
	'accept-encoding': 'gzip, deflate, br',
	'accept-language': 'zh-CN,zh;q=0.9',
	'cookie': '__cfduid=d5ba7767240ad891251e23052ba6dd2d31546074489; has_js=1; _ga=GA1.2.2020405756.1546074488; _gid=GA1.2.962559095.1546074488; __gads=ID=74557f7e9b4162db:T=1546074493:S=ALNI_MYYNLzFSq6eH1mnzkdW7u0oaSIbsA; cb-enabled=enabled; _pk_ses.3.5465=*; _pk_id.3.5465=ed8e7f2ed2573eee.1546074495.1.1546074800.1546074495.',
	'referer': 'https://www.etf.com/etfanalytics/etf-finder',
	'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
	'x-newrelic-id': 'UgcAVlBUGwQFU1NWAAUD',
	'x-requested-with': 'XMLHttpRequest'
}

def getPage(page_num, page_limit):
	url = 'https://www.etf.com/etf-finder-funds-api//-aum/'
	url = url + str(page_num * page_limit)
	url = url + '/'
	url = url + str(page_limit)
	url = url + '/1'
	response = requests.get(url, headers=headers)
	return response.status_code, response.text, response.headers, response.cookies

# 根据key从data中取值
def getValue(data, key):
	if data is not None:
		return data.get(key, '')
	else:
		return ''

def parseFundBasics(data):
	fundBasics = []
	if data is not None:
		issuer = getValue(data, 'issuer')
		issuer = re.sub(r'<.*?>', '', issuer)
		fundBasics.append(issuer)
		fundBasics.append(getValue(getValue(data, 'expenseRatio'), 'value'))
		fundBasics.append(getValue(getValue(data, 'aum'), 'value'))
		fundBasics.append(getValue(getValue(data, 'spreadPct'), 'value'))
		fundBasics.append(getValue(data, 'segment'))
	return fundBasics

def parsePerformance(data):
	performance = []
	if data is not None:
		performance.append(getValue(getValue(data, 'priceTr1Mo'), 'value'))
		performance.append(getValue(getValue(data, 'priceTr3Mo'), 'value'))
		performance.append(getValue(getValue(data, 'priceTr1Yr'), 'value'))
		performance.append(getValue(getValue(data, 'priceTr3YrAnnualized'), 'value'))
		performance.append(getValue(getValue(data, 'priceTr5YrAnnualized'), 'value'))
		performance.append(getValue(getValue(data, 'priceTr10YrAnnualized'), 'value'))
		performance.append(getValue(data, 'priceTrAsOf'))
	return performance

def parseAnalysis(data):
	analysis = []
	if data is not None:
		analysis.append(getValue(data, 'analystPick'))
		analysis.append(getValue(data, 'letterGrade'))
		analysis.append(getValue(data, 'efficiencyScore'))
		analysis.append(getValue(data, 'tradabilityScore'))
		analysis.append(getValue(data, 'fitScore'))
		analysis.append(getValue(data, 'avgDailyDollarVolume'))
		analysis.append(getValue(data, 'avgDailyShareVolume'))
		analysis.append(getValue(data, 'fundClosureRisk'))
	return analysis

def parseFundamentals(data):
	fundamentals = []
	if data is not None:
		fundamentals.append(getValue(getValue(data, 'dividendYield'), 'value'))
		equity = getValue(data, 'equity')
		fundamentals.append(getValue(equity, 'pe'))
		fundamentals.append(getValue(equity, 'pb'))
		fixedIncome = getValue(data, 'fixedIncome')
		fundamentals.append(getValue(fixedIncome, 'duration'))
		fundamentals.append(getValue(fixedIncome, 'creditQuality'))
		fundamentals.append(getValue(getValue(fixedIncome, 'ytm'), 'value'))
	return fundamentals

def parseClassification(data):
	classification = []
	if data is not None:
		classification.append(getValue(data, 'assetClass'))
		classification.append(getValue(data, 'strategy'))
		classification.append(getValue(data, 'region'))
		classification.append(getValue(data, 'geography'))
		classification.append(getValue(data, 'category'))
		classification.append(getValue(data, 'focus'))
		classification.append(getValue(data, 'niche'))
		classification.append(getValue(data, 'inverse'))
		classification.append(getValue(data, 'leveraged'))
		classification.append(getValue(data, 'etn'))
		classification.append(getValue(data, 'selectionCriteria'))
		classification.append(getValue(data, 'weightingScheme'))
		classification.append(getValue(data, 'activePerSec'))
		classification.append(getValue(data, 'underlyingIndex'))
		classification.append(getValue(data, 'indexProvider'))
		classification.append(getValue(data, 'brand'))
	return classification

def parseTax(data):
	tax = []
	if data is not None:
		tax.append(getValue(data, 'legalStructure'))
		tax.append(getValue(data, 'maxLtCapitalGainsRate'))
		tax.append(getValue(data, 'maxStCapitalGainsRate'))
		tax.append(getValue(data, 'taxReporting'))
	return tax

def parseEsg(data):
	esg = []
	if data is not None:
		esg.append(getValue(data, 'msciEsgQualityScore'))
		esg.append(getValue(data, 'msciEsgQualityScorePctlPeer'))
		esg.append(getValue(data, 'msciEsgQualityScorePctlGlobal'))
		esg.append(getValue(data, 'msciWeightedAvgCarbonInten'))
		esg.append(getValue(data, 'msciSustainableImpactPct'))
		esg.append(getValue(data, 'msciSriExclusionCriteriaPct'))
		esg.append(getValue(data, 'msciEsgHasBadge'))
	return esg

def getListValue(list, index):
	if len(list) > index :
		return list[index]
	else:
		return ''

def addSheetTitle(sheet, title):
	for i in range(len(title)):
		sheet.write(0, i, title[i])

def addSheetLine(sheet, lin_num, line_data):
	for i in range(len(line_data)):
		sheet.write(lin_num, i, line_data[i])

def spide():
	num = 1
	page_num = 0
	total_num = 2212
	limit = 50
	fail_time = 0
	while num <= total_num:
		code, text, h, cookies = getPage(page_num, limit)
		if code == 200:
			content = json.loads(text)
			num = num + parse_and_save_conent(num, content)
			print('已经成功爬取了', num-1, '条数据')
			page_num = page_num + 1
			time.sleep(1)
		else:
			if code == 429:
				print('停止爬取数据, status_code = ', code)
				print('Retry-After', h.get('Retry-After', '-1'))
				break
			fail_time = fail_time + 1
			if fail_time >= 3:
				print('停止爬取数据, status_code = ', code)
				break
	print('爬取数据结束！')
	book.save('etf.xls') # 保存excel

# 解析每一页的数据，并存储到Excel表中
def parse_and_save_conent(num, content):
	for item in content:
		productId = getValue(item, 'productId')
		fund = getValue(item, 'fund')
		ticker = getValue(item, 'ticker')
		inceptionDate = getValue(item, 'inceptionDate')
		launchDate = getValue(item, 'launchDate')
		hasSegmentReport = getValue(item, 'hasSegmentReport')
		genericReport = getValue(item, 'genericReport')
		hasReport = getValue(item, 'hasReport')
		fundsInSegment = getValue(item, 'fundsInSegment')
		economicDevelopment = getValue(item, 'economicDevelopment')
		totalRows = getValue(item, 'totalRows')

		fundBasics = parseFundBasics(getValue(item, 'fundBasics'))
		fundBasics.insert(0, ticker)
		fundBasics.insert(1, fund)
		# print(fundBasics)
		addSheetLine(sheet_fundBasics, num, fundBasics)


		performance = parsePerformance(getValue(item, 'performance'))
		performance.insert(0, ticker)
		performance.insert(1, fund)
		# print(performance)
		addSheetLine(sheet_performance, num, performance)

		analysis = parseAnalysis(getValue(item, 'analysis'))
		analysis.insert(0, ticker)
		analysis.insert(1, fund)
		analysis.insert(2, getListValue(fundBasics, 2))
		analysis.insert(3, getListValue(fundBasics, 6))
		# print(analysis)
		addSheetLine(sheet_analysis, num, analysis)

		fundamentals = parseFundamentals(getValue(item, 'fundamentals'))
		fundamentals.insert(0, ticker)
		fundamentals.insert(1, fund)
		# print(fundamentals)
		addSheetLine(sheet_fundamentals, num, fundamentals)

		classification = parseClassification(getValue(item, 'classification'))
		classification.insert(0, ticker)
		classification.insert(1, fund)
		# print(classification)
		addSheetLine(sheet_classification, num, classification)

		tax = parseTax(getValue(item, 'tax'))
		tax.insert(0, ticker)
		tax.insert(1, fund)
		addSheetLine(sheet_tax, num, tax)

		esg = parseEsg(getValue(item, 'msciEsg'))
		esg.insert(0, ticker)
		esg.insert(1, fund)
		addSheetLine(sheet_esg, num, esg)

		num = num + 1
	return len(content)


# 创建一个excel对象
book = xlwt.Workbook()
sheet_fundBasics = book.add_sheet('fund basics', cell_overwrite_ok=True) # 添加一个sheet页
sheet_performance = book.add_sheet('performance', cell_overwrite_ok=True)
sheet_analysis = book.add_sheet('analysis', cell_overwrite_ok=True)
sheet_fundamentals = book.add_sheet('fundamentals', cell_overwrite_ok=True)
sheet_classification = book.add_sheet('classification', cell_overwrite_ok=True)
sheet_tax = book.add_sheet('tax', cell_overwrite_ok=True)
sheet_esg = book.add_sheet('esg', cell_overwrite_ok=True)

addSheetTitle(sheet_fundBasics, ['ticker', 'fund name', 'issuer', 'expense ratio', 'aum', 'spread', 'segment'])
addSheetTitle(sheet_performance,['ticker', 'fund name', '1 month', '3 month', '1 year', '3 year', '5 year', '10 year', 'as of'])
addSheetTitle(sheet_analysis, ['ticker', 'fund name', 'issuer', 'segment', 'analysis pick', 'grade', 'efficiencyScore', 'tradabilityScore', 'fitScore', 'avgDailyDollarVolume', 'avgDailyShareVolume', 'fundClosureRisk'])
addSheetTitle(sheet_fundamentals, ['ticker', 'fund name', 'dividend yield', 'P/E', 'P/B', 'duration', 'credit quality', 'ytm'])
addSheetTitle(sheet_classification, ['ticker', 'fund name', 'asset class', 'strategy', 'region', 'geography', 'category', 'focus', 'niche', 'inverse', 'leveraged', 'etn', 'selection criteria', 'weighting scheme', 'active per sec', 'underlying index', 'index provider', 'brand'])
addSheetTitle(sheet_tax, ['ticker', 'fund name', 'legal structure', 'max lt capital gains rate', 'max st capital gains rate', 'tax reporting'])
addSheetTitle(sheet_esg, ['ticker', 'fund name', 'msciEsgQualityScore', 'msciEsgQualityScorePctlPeer', 'msciEsgQualityScorePctlGlobal', 'msciWeightedAvgCarbonInten', 'msciSustainableImpactPct', 'msciSriExclusionCriteriaPct', 'msciEsgHasBadge'])

# 开启一个线程爬取数据
t = threading.Thread(target = spide)
t.start()


