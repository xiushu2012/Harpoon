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


if __name__=='__main__':

		from sys import argv

		bondarray = []
		if len(argv) > 1:
			bondarray = [stock for stock in argv[1:]]
		else:
			print("please run like 'python Volume.py [sh113542]'")
			exit(1)

		bond_kelly_df = pd.DataFrame(columns=['可转债','赔率','胜率','下注比例','当前价格','25分位','50分位','75分位'])
		for bond in bondarray:
			dailypath =  "./bond/%s.xls" % (bond)
			resultpath,insheetname = get_akshare_daily(dailypath,bond)
			print("data of path:" + resultpath + ",sheetname:" +insheetname)

			bond_cov_daily_df = pd.read_excel(resultpath, insheetname)[['date', 'close']]
			dailysta = bond_cov_daily_df['close'].describe()
			#print(dailysta)
			counts = dailysta['count']
			date = bond_cov_daily_df.loc[counts-1][0]
			value = bond_cov_daily_df.loc[counts-1][1]



			value25 = dailysta['25%']
			value75 = dailysta['75%']
			value50 = dailysta['50%']
			#赔率=获胜时的盈利/失败时的亏损
			kellyb = (value75-value)/(value - value25)

			print("value25 and value75:", value25, value75)

			price =  bond_cov_daily_df['close']
			wincounts = price[ price > value ].count()
			#成功总次数/(成功总次数+失败总次数)
			kellyp = wincounts / counts

			#下注比例
			kellyf = ((kellyb+1)*kellyp-1)/kellyb
			bond_kelly_df = bond_kelly_df.append({'可转债':bond,'赔率':kellyb,'胜率':kellyp,'下注比例':kellyf,'当前价格':value,'25分位':value25,'50分位':value50,'75分位':value75},ignore_index=True)
			print("可转债,赔率,胜率,下注比例:",bond,kellyb,kellyp,kellyf)
		#print(bond_kelly_df)
		tnow = datetime.datetime.now()
		fileout = tnow.strftime('%Y_%m_%d') + '_kelly.xls'
		outanalypath = "%s/%s" % ('bond', fileout)
		writer = pd.ExcelWriter(outanalypath)
		bond_kelly_df.to_excel(writer, 'kelly')
		writer.save()
		print("kelly analy out path:" + outanalypath)






