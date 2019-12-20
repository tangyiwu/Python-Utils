#!/usr/bin/env python
# -*- coding:utf-8 -*-

def get_interests(base, rate, years):
	money = 0
	for x in range(years):
		money = (money + base) * (1 + rate)
	return money

def main():
	base = float(input('请输入每年金额:'))
	rate = float(input('请输入年利率:'))
	years = int(input('请输入年数:'))
	# money = get_interests(24550, 0.01, 20)
	money = get_interests(base, rate, years)
	print("到期本金为：%.2f元" % money)

if __name__ == '__main__':
	main()