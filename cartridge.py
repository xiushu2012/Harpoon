﻿# -*- coding: utf-8 -*-

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
from sklearn.cluster import DBSCAN

def get_akshare_daily(stock,end):
	xlsfile =  "./bond/primary/%s.xlsx" % (bond)
	
	datefolder = r'./bond/' + end
	folderExist = os.path.exists(datefolder)
	if not folderExist:
			os.makedirs(datefolder)
			print("daily:%s create" % (datefolder))
	else:
			print("daily:%s exist" % (datefolder))
	outfile = "./%s/%s.xlsx" % (datefolder,bond)
	shname='daily'
	
	isExist = os.path.exists(xlsfile)
	#dateend = end
	dateend = datetime.datetime.strptime(end,'%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S")
	
	if not isExist:
		bond_zh_hs_cov_daily_df = ak.bond_zh_hs_cov_daily(symbol=stock)
		bond_zh_hs_cov_daily_df.to_excel(xlsfile,sheet_name=shname)
		print("xfsfile:%s create" % (xlsfile))
		
		bond_zh_hs_cov_daily_df = pd.read_excel(xlsfile, sheet_name=shname,index_col=0,converters={'date': str})
		bond_zh_hs_cov_daily_df = bond_zh_hs_cov_daily_df[ bond_zh_hs_cov_daily_df['date'] <= dateend ]
		if bond_zh_hs_cov_daily_df.empty:
			raise ValueError('no data before ' + end)
		bond_zh_hs_cov_daily_df.to_excel(outfile,sheet_name=shname)
		print("xfsfile:%s create" % (outfile))  
	else:
		bond_zh_hs_cov_daily_df = pd.read_excel(xlsfile, sheet_name=shname,index_col=0,converters={'date': str})
		bond_zh_hs_cov_daily_df = bond_zh_hs_cov_daily_df[ bond_zh_hs_cov_daily_df['date'] <= dateend ]
		if bond_zh_hs_cov_daily_df.empty:
			raise ValueError('no data before ' + end)
		bond_zh_hs_cov_daily_df.to_excel(outfile,sheet_name=shname)
		print("xfsfile:%s create" % (outfile))
	return outfile,shname

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


def cal_close_inc(volume_df,close):
	for i,r in volume_df.iterrows():
			if r[datecolumn] == date:
				return r[mvcolumn]
	return 0

def get_dailyinc_df(path,name,ratio):
	bond_cov_dailyinc_df = pd.read_excel(path, name)[['date', 'open','high']]
	bond_cov_dailyinc_df[ratio] = bond_cov_dailyinc_df.apply(lambda row: (row['high']-row['open'])/row['open'], axis=1)
	bond_cov_biginc_df = bond_cov_dailyinc_df[ bond_cov_dailyinc_df[ratio] > 0.03]
	return bond_cov_biginc_df

def get_abnormal_dbscan_df(path,name):
	bond_cov_volume_df = pd.read_excel(path, name)[['date','open','high','low','close','volume']]
	volumesta = bond_cov_volume_df['volume'].describe(percentiles = [0.3,0.7])
	valuelow =  volumesta['30%']
	valuehigh = volumesta['70%']
	middle_volume_df = bond_cov_volume_df[ (bond_cov_volume_df[['volume']] < valuehigh) & (bond_cov_volume_df[['volume']] > valuelow)]
	
	middlesta = middle_volume_df['volume'].describe()
	middlepes = middlesta['std']
	print("valuelow:%f,valuehigh:%f,EPS:%f" %(valuelow,valuehigh,middlepes))
	

	outlier_det=DBSCAN(min_samples=2,eps=middlepes)
	clusters = outlier_det.fit_predict(bond_cov_volume_df[['volume']].values)
	print("abnormal volumn:%d" % list(clusters).count(-1))
	bond_cov_volume_df['flag'] = clusters

	
	bond_cov_abnormal_df = bond_cov_volume_df[ bond_cov_volume_df['flag'] == -1]
	
	
	abnormal_index = bond_cov_abnormal_df.index.values.tolist()
	for cur, nxt in zip (abnormal_index, abnormal_index [1:] ):
		print (cur, nxt)

		#左右都闭区间
		abnormal_next_df = bond_cov_volume_df.loc[cur:nxt,:][['open','high','low','close']]
		#cur当天数据不能纳入计算
		abnormal_next_array = abnormal_next_df.values[1::,:]
		#print(abnormal_next_array)
		abnormal_cur_close =  abnormal_next_df.loc[cur,'close']

		bond_cov_abnormal_df.loc[cur,'max'] = 100*(np.max(abnormal_next_array)-abnormal_cur_close)/abnormal_cur_close
		bond_cov_abnormal_df.loc[cur,'min'] = 100*(np.min(abnormal_next_array)-abnormal_cur_close)/abnormal_cur_close

	#print(bond_cov_volume_df)
	if not os.path.exists(path):
		bond_cov_abnormal_df.to_excel(writer, 'abnormal')
	else:
		with pd.ExcelWriter(path,engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
			bond_cov_abnormal_df.to_excel(writer, 'abnormal')	
	return bond_cov_abnormal_df


def get_abnormal_standard_df(path,name):
	bond_cov_volume_df = pd.read_excel(path, name)[['date','volume']]

	volume_std = np.std(bond_cov_volume_df[['volume']])
	volume_mean = np.mean(bond_cov_volume_df[['volume']])
	volume_cutoff = volume_std*1
	volume_low = volume_mean - volume_cutoff
	volume_high = volume_mean + volume_cutoff
	print(volume_low,volume_high)


	bond_cov_volume_df = bond_cov_volume_df[ (bond_cov_volume_df[['volume']] < volume_low) | (bond_cov_volume_df[['volume']] > volume_high)]
	print(bond_cov_volume_df)
	
	if not os.path.exists(path):
		bond_cov_volume_df.to_excel(writer, 'abnormal',index=False)
	else:
		with pd.ExcelWriter(path,engine='openpyxl',mode='a') as writer:
			bond_cov_volume_df.to_excel(writer, 'abnormal',index=False)	
	return bond_cov_volume_df


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


def select_interest_some(writer,bond_expect_df,tag):
		bond_expect_df = bond_expect_df.sort_values('下注比例', ascending=False)
		bond_expect_df.to_excel(writer, tag)
		optimaltag = 'opt-'+ tag;
		bond_expect_selected_df = bond_expect_df[(bond_expect_df['年均异动'] >= 7.0) & (bond_expect_df['下注比例'] >= 0.3) & (bond_expect_df['交易周期'] >= 1)]
		bond_expect_selected_df = bond_expect_selected_df.sort_values('年均异动', ascending=False)
		bond_expect_selected_df.to_excel(writer, optimaltag)

if __name__=='__main__':
		from sys import argv
		interestpath = ''
		today = datetime.datetime.now()
		if len(argv) > 2:
			if argv[2] == '*':
				today = datetime.datetime.now().strftime('%Y-%m-%d')
			else:
				today = datetime.datetime.strptime(argv[2], '%Y-%m-%d').strftime('%Y-%m-%d')
			print('today'+ today)
			
			interestpath = argv[1]
			isExist = os.path.exists(interestpath)
			if not isExist:
				print("please make sure the path:" + interestpath)
				exit(1)
		else:
			print("please run like 'python cartridge.py [file] [2022-08-22]'")
			exit(1)

		bond_interest_df = pd.read_excel(interestpath, 'clause')


		bond_kelly_df = pd.DataFrame(columns=['名称', '代码', '胜率', '赔率', '下注比例', '当前价格', '00分位', '25分位', '50分位', '75分位', '100分位', '75涨幅','交易周期','年均异动','最后异动','异动阈值'])
		money = 'money'
		ratio = 'ratio'
		for i, bondrow in bond_interest_df.iterrows():
			name = bondrow['name'];bond = bondrow['code'];

			try:
				resultpath,insheetname = get_akshare_daily(bond,today)
			except Exception as result:
				print(bond + " get bond error:" + str(result))
				continue
			print("get datapath ok:" + resultpath + ",sheetname:" +insheetname)



			#bond_cov_daily_df = pd.read_excel(resultpath, insheetname)[['date', 'close']]
			#dailysta = bond_cov_daily_df['close'].describe()
			bond_cov_daily_df = get_daily_df(resultpath, insheetname, money)
			dailysta = bond_cov_daily_df[money].describe()

			bond_cov_biginc_df = get_dailyinc_df(resultpath, insheetname,ratio)
			incsta = bond_cov_biginc_df[ratio].describe()
			
			print(dailysta)
			print(incsta)

			counts = dailysta['count']
			tradeyears  =  counts/4/250

			date = bond_cov_daily_df.loc[counts-1][0]
			value = bond_cov_daily_df.loc[counts-1][1]

			valuemin = dailysta['min']
			valuemax = dailysta['max']
			value25 = dailysta['25%']
			value50 = dailysta['50%']
			value75 = dailysta['75%']

			inc75 = incsta['75%']
			# 赔率=获胜时的盈利/失败时的亏损
			kellyb1= getkellybEx(value,valuemin,valuemax)

			price =  bond_cov_daily_df[money]
			wincounts = price[ price > value ].count()
			#成功总次数/(成功总次数+失败总次数)
			kellyp = wincounts / counts

			#下注比例
			kellyf1 = ((kellyb1+1)*kellyp-1)/kellyb1

			#异动指标
			try:
				bond_cov_abnormal_df = get_abnormal_dbscan_df(resultpath,insheetname)
				abnormalcount = len(bond_cov_abnormal_df)
				print("abnormalcount:%d" % abnormalcount)
				#250个交易日
				abnormalperyear = abnormalcount/tradeyears
				abnormallatest = bond_cov_abnormal_df.iloc[-1][0]
				abnormalminvol = np.min(bond_cov_abnormal_df['volume'])
				#print("--->"+str(abnormalminvol))
			except Exception as result:
				print("get abnormal error:" + bond)
				continue

			bond_kelly_df = bond_kelly_df.append({'名称':name,'代码':bond,'胜率':kellyp,'赔率':kellyb1,'下注比例':kellyf1,
			'当前价格':value,'00分位':valuemin,'25分位':value25,'50分位':value50,'75分位':value75,'100分位':valuemax,'75涨幅':inc75,
			'交易周期':tradeyears,'年均异动':abnormalperyear,'最后异动':abnormallatest,'异动阈值':abnormalminvol},ignore_index=True)

			print("名称,胜率，赔率,下注比例:",name,kellyp,kellyb1,kellyf1)
		#print(bond_kelly_df)

		fileout = today + '_kelly.xlsx'
		outanalypath = "%s/%s" % ('bond', fileout)
		writer = pd.ExcelWriter(outanalypath)
		#bond_kelly_df.to_excel(writer, 'kelly')
		select_interest_some(writer, bond_kelly_df, 'kelly')
		writer.save()
		print("kelly analy out path:" + outanalypath)






