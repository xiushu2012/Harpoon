# -*- coding: utf-8 -*-

import akshare as ak
import numpy as np  
import pandas as pd  
import math
import datetime
import os
import matplotlib.pyplot as plt
import openpyxl


# -*- coding: utf-8 -*-

import akshare as ak
import numpy as np  
import pandas as pd  
import math
import datetime
import os
import matplotlib.pyplot as plt
import openpyxl

def get_akshare_daily(xlsfile,stock):
	shname='daily'
	isExist = os.path.exists(xlsfile)
	if not isExist:
		bond_zh_hs_cov_daily_df = ak.bond_zh_hs_cov_daily(symbol=stock)
		bond_zh_hs_cov_daily_df.to_excel(xlsfile,sheet_name=shname)
		
		print("xfsfile:%s create" % (xlsfile))  
	else:
		print("xfsfile:%s exist" % (xlsfile))
	
	return xlsfile,shname

def getkellyb(value,v0,v25,v50,v75):
	# 赔率=获胜时的盈利/失败时的亏损
	kellyb1 = 0.01
	kellyb2 = 0.01
	if value <= v0:
		kellyb1 = (v50 - value) / (value - 1)
		kellyb2 = (v75 - value) / (value - 1)
	elif value > v0  and  value <= v50:
		kellyb1 = (v50 - value) / (value - v0)
		kellyb2 = (v75 - value) / (value - v0)
	else:
		kellyb1 = 0.01
		kellyb2 = 0.01
	print("valule0,value25,value50,value75:", v0,v25,v50,v75)
	return kellyb1,kellyb2

def getkellybEx(value,v0,v100):
	# 赔率=获胜时的盈利/失败时的亏损
	kellyb = 0.01
	if value <= v0:
		kellyb = (v100 - value) / (value - 1)
	else:
		kellyb = (v100 - value) / (value - v0)
	print("valule0,value100:", v0,v100)
	return kellyb


def get_daily_df(path,name,price):
	newcolumn = price
	bond_cov_daily_df_open = pd.read_excel(path, name)[['date', 'open']]
	lenopen = len(bond_cov_daily_df_open);
	bond_cov_daily_df_open.index = range(0, lenopen)
	bond_cov_daily_df_open = bond_cov_daily_df_open.rename(columns={'open':newcolumn})

	bond_cov_daily_df_low = pd.read_excel(path, name)[['date', 'low']]
	lenlow = len(bond_cov_daily_df_low);
	bond_cov_daily_df_low.index = range(lenopen, lenopen + lenlow)
	bond_cov_daily_df_low = bond_cov_daily_df_low.rename(columns={'low': newcolumn})

	bond_cov_daily_df_high = pd.read_excel(path, name)[['date', 'high']]
	lenhigh = len(bond_cov_daily_df_high);
	bond_cov_daily_df_high.index = range(lenopen + lenlow, lenopen + lenlow + lenhigh)
	bond_cov_daily_df_high = bond_cov_daily_df_high.rename(columns={'high': newcolumn})

	bond_cov_daily_df_close = pd.read_excel(path, name)[['date', 'close']]
	lenclose = len(bond_cov_daily_df_close);
	bond_cov_daily_df_close.index = range(lenopen + lenlow + lenhigh, lenopen + lenlow + lenhigh + lenclose)
	bond_cov_daily_df_close = bond_cov_daily_df_close.rename(columns={'close': newcolumn})

	bond_cov_daily_df = pd.concat([bond_cov_daily_df_open, bond_cov_daily_df_low, bond_cov_daily_df_high, bond_cov_daily_df_close])
	return bond_cov_daily_df


if __name__=='__main__':

		interestpath = "./interest.xlsx"
		isExist = os.path.exists(interestpath)
		if not isExist:
			print("please make sure the ./interest.xlsx")
			exit(1)

		bond_interest_df = pd.read_excel(interestpath, 'clause')

		bond_kelly_df = pd.DataFrame(columns=['名称','代码', '胜率', '赔率', '下注比例', '当前价格', '00分位', '25分位', '50分位', '75分位','100分位'])
		money = 'money'
		for i, bondrow in bond_interest_df.iterrows():
			name = bondrow['name'];bond = bondrow['code'];

			dailypath =  "./bond/%s.xlsx" % (bond)
			resultpath,insheetname = get_akshare_daily(dailypath,bond)
			print("data of path:" + resultpath + ",sheetname:" +insheetname)


			#bond_cov_daily_df = pd.read_excel(resultpath, insheetname)[['date', 'close']]
			#dailysta = bond_cov_daily_df['close'].describe()
			bond_cov_daily_df = get_daily_df(resultpath, insheetname, money)
			dailysta = bond_cov_daily_df[money].describe()

			print(dailysta)
			counts = dailysta['count']
			date = bond_cov_daily_df.loc[counts-1][0]
			value = bond_cov_daily_df.loc[counts-1][1]

			valuemin = dailysta['min']
			valuemax = dailysta['max']
			value25 = dailysta['25%']
			value50 = dailysta['50%']
			value75 = dailysta['75%']

			# 赔率=获胜时的盈利/失败时的亏损
			kellyb1= getkellybEx(value,valuemin,valuemax)

			price =  bond_cov_daily_df[money]
			wincounts = price[ price > value ].count()
			#成功总次数/(成功总次数+失败总次数)
			kellyp = wincounts / counts

			#下注比例
			kellyf1 = ((kellyb1+1)*kellyp-1)/kellyb1

			bond_kelly_df = bond_kelly_df.append({'名称':name,'代码':bond,'胜率':kellyp,'赔率':kellyb1,'下注比例':kellyf1,'当前价格':value,'00分位':valuemin,'25分位':value25,'50分位':value50,'75分位':value75,'100分位':valuemax},ignore_index=True)

			print("名称,胜率，赔率,下注比例:",name,kellyp,kellyb1,kellyf1)
		#print(bond_kelly_df)
		tnow = datetime.datetime.now()
		fileout = tnow.strftime('%Y_%m_%d') + '_kelly.xlsx'
		outanalypath = "%s/%s" % ('bond', fileout)
		writer = pd.ExcelWriter(outanalypath)
		bond_kelly_df.to_excel(writer, 'kelly')
		writer.save()
		print("kelly analy out path:" + outanalypath)






