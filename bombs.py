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
import time
import warnings
from pandas.core.generic import SettingWithCopyWarning

def get_akshare_daily(stock,end):
	xlsfile =  "./bond/primary/%s_trade.xlsx" % (stock)
	datefolder = r'./bond/' + end
	outfile = "./%s/%s_trade.xlsx" % (datefolder,stock)
	shname='trade'
	
	folderExist = os.path.exists(datefolder)
	if not folderExist:
			os.makedirs(datefolder)
			print("daily:%s create" % (datefolder))
	else:
			print("daily:%s exist" % (datefolder))

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

def get_akshare_valanaly(stock,end):
	xlsfile =  "./bond/primary/%s_valanaly.xlsx" % (stock)
	datefolder = r'./bond/' + end
	outfile = "./%s/%s_valanaly.xlsx" % (datefolder,stock)
	shname='valanaly'
	
	folderExist = os.path.exists(datefolder)
	if not folderExist:
			os.makedirs(datefolder)
			print("daily:%s create" % (datefolder))
	else:
			print("daily:%s exist" % (datefolder))

	
	isExist = os.path.exists(xlsfile)
	#dateend = end
	dateend = datetime.datetime.strptime(end,'%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S")
	
	if not isExist:
		bond_zh_cov_value_analysis_df = ak.bond_zh_cov_value_analysis(symbol=stock)
		bond_zh_cov_value_analysis_df.to_excel(xlsfile,sheet_name=shname)
		print("xfsfile:%s create" % (xlsfile))
		bond_zh_cov_value_analysis_df = pd.read_excel(xlsfile, sheet_name=shname,index_col=0,converters={'日期': str})
		bond_zh_cov_value_analysis_df = bond_zh_cov_value_analysis_df[ bond_zh_cov_value_analysis_df['日期'] <= dateend ]
		if bond_zh_cov_value_analysis_df.empty:
			raise ValueError('no data before ' + end)
		bond_zh_cov_value_analysis_df.to_excel(outfile,sheet_name=shname)
		print("xfsfile:%s create" % (outfile))  
	else:
		bond_zh_cov_value_analysis_df = pd.read_excel(xlsfile, sheet_name=shname,index_col=0,converters={'日期': str})
		bond_zh_cov_value_analysis_df = bond_zh_cov_value_analysis_df[ bond_zh_cov_value_analysis_df['日期'] <= dateend ]
		if bond_zh_cov_value_analysis_df.empty:
			raise ValueError('no data before ' + end)
		bond_zh_cov_value_analysis_df.to_excel(outfile,sheet_name=shname)
		print("xfsfile:%s create" % (outfile))
	return outfile,shname

def getkellybEx(value,expval,maxval,ltyear):
	# 赔率=获胜时的净盈利/成本
	# 利息损失 = (value*(1+大额存单利率)**2 -value) - (value*(1+到期利率)**2 - value)
	deficit = value*(1+0.03)**ltyear - expval
	kellyb = 0.01
	if deficit <= 1:
		kellyb = (maxval-value-deficit)/1
	else:
		kellyb = (maxval-value-deficit)/deficit

	#print("kellyb:%f" % (kellyb))
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

def get_crash_dbscan_df(path,name):
	bond_cov_crash_df = pd.read_excel(path, name)[['date','open','high','low','close','volume']]
	bond_cov_crash_df = bond_cov_crash_df[ bond_cov_crash_df['open'] < 121 ]
	bond_cov_crash_df['crash'] = bond_cov_crash_df.apply(lambda row: 100*(row['low']-row['open'])/row['open'], axis=1)

	#print(bond_cov_crash_df)
	crashsta = bond_cov_crash_df['crash'].describe(percentiles = [0.3,0.7])
	crashlow =  crashsta['30%']
	crashhigh = crashsta['70%']
	middle_crash_df = bond_cov_crash_df[ (bond_cov_crash_df[['crash']] < crashhigh) & (bond_cov_crash_df[['crash']] > crashlow)]
	
	middlesta = middle_crash_df['crash'].describe()

	middlepes = middlesta['std']
	print("crashlow:%f,crashhigh:%f,EPS:%f" %(crashlow,crashhigh,middlepes))
	
	#first cluster to find abnormal days
	outlier_det=DBSCAN(min_samples=2,eps=middlepes)
	clusters = outlier_det.fit_predict(bond_cov_crash_df[['crash']].values)
	print("abnormal crash count:%d" % list(clusters).count(-1))
	bond_cov_crash_df['flag'] = clusters

	
	bond_cov_collapse_df = bond_cov_crash_df[ bond_cov_crash_df['flag'] == -1]
	
	#second cluster to cut abnormaldays to several paragraph
	bond_cov_collapse_df['ts'] = bond_cov_collapse_df.apply(lambda row: time.mktime(time.strptime(str(row['date']),"%Y-%m-%d %H:%M:%S")), axis=1)
	#print(bond_cov_collapse_df[['ts']].values)
	abnlier_det=DBSCAN(min_samples=2,eps=7*86400)
	bond_cov_collapse_df['type'] = abnlier_det.fit_predict(bond_cov_collapse_df[['ts']].values.astype(int))
	#print(abnormal_df['type'])
	
	if not os.path.exists(path):
		bond_cov_collapse_df.to_excel(writer, 'crash')
	else:
		with pd.ExcelWriter(path,engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
			bond_cov_collapse_df.to_excel(writer, 'crash')	
	return bond_cov_collapse_df

def get_abnormal_dbscan_df(path,name):
	bond_cov_volume_df = pd.read_excel(path, name)[['date','open','high','low','close','volume']]
	volumesta = bond_cov_volume_df['volume'].describe(percentiles = [0.3,0.7])
	valuelow =  volumesta['30%']
	valuehigh = volumesta['70%']
	middle_volume_df = bond_cov_volume_df[ (bond_cov_volume_df[['volume']] < valuehigh) & (bond_cov_volume_df[['volume']] > valuelow)]
	
	middlesta = middle_volume_df['volume'].describe()
	middlepes = middlesta['std']
	print("volumnlow:%f,volumnhigh:%f,EPS:%f" %(valuelow,valuehigh,middlepes))
	
	#first cluster to find abnormal days
	outlier_det=DBSCAN(min_samples=2,eps=middlepes)
	clusters = outlier_det.fit_predict(bond_cov_volume_df[['volume']].values)
	print("abnormal volumn count:%d" % list(clusters).count(-1))
	bond_cov_volume_df['flag'] = clusters

	
	bond_cov_abnormal_df = bond_cov_volume_df[ bond_cov_volume_df['flag'] == -1]
	
	
	abnormal_index = bond_cov_abnormal_df.index.values.tolist()
	for cur, nxt in zip (abnormal_index, abnormal_index [1:] ):
		#print (cur, nxt)

		#左右都闭区间
		abnormal_next_df = bond_cov_volume_df.loc[cur:nxt,:][['open','high','low','close']]
		#cur当天数据不能纳入计算
		abnormal_next_array = abnormal_next_df.values[1::,:]
		#print(abnormal_next_array)
		abnormal_cur_close =  abnormal_next_df.loc[cur,'close']

		bond_cov_abnormal_df.loc[cur,'max'] = 100*(np.max(abnormal_next_array)-abnormal_cur_close)/abnormal_cur_close
		bond_cov_abnormal_df.loc[cur,'min'] = 100*(np.min(abnormal_next_array)-abnormal_cur_close)/abnormal_cur_close

	#second cluster to cut abnormaldays to several paragraph
	bond_cov_abnormal_df['ts'] = bond_cov_abnormal_df.apply(lambda row: time.mktime(time.strptime(str(row['date']),"%Y-%m-%d %H:%M:%S")), axis=1)
	#print(abnormal_df[['ts']].values)
	abnlier_det=DBSCAN(min_samples=2,eps=7*86400)
	bond_cov_abnormal_df['type'] = abnlier_det.fit_predict(bond_cov_abnormal_df[['ts']].values.astype(int))
	#print(abnormal_df['type'])
	
	#print(bond_cov_volume_df)
	if not os.path.exists(path):
		bond_cov_abnormal_df.to_excel(writer, 'abnormal')
	else:
		with pd.ExcelWriter(path,engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
			bond_cov_abnormal_df.to_excel(writer, 'abnormal')	
	return bond_cov_abnormal_df


def guess_abnormal_parameter_additional(abnormal_df,tradeyear):

	element_counts = abnormal_df['type'].value_counts()
	#print(element_counts)

	oneshotcount = 0
	totalcount   = 0
	if -1 in element_counts:
		oneshotcount = element_counts[-1]
		totalcount = len(element_counts)- 1 + oneshotcount
	else:
		totalcount = len(element_counts)

	abnperyear = totalcount/tradeyear
	
	#假设每年只取一次波动，那么该异动涨幅应该位于所有波动的前1/abnperyear分位
	rate = abnormal_df.apply(lambda row: 100*(row['high']-row['open'])/row['open'], axis=1)
	abnrate = rate.quantile(1-1/abnperyear)
	
	return abnperyear,abnrate



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
	bond_cov_daily_df_open = pd.read_excel(path, name)[['date', 'open']]
	lenopen = len(bond_cov_daily_df_open);
	bond_cov_daily_df_open.index = range(0, lenopen)
	bond_cov_daily_df_open = bond_cov_daily_df_open.rename(columns={'open':price})

	bond_cov_daily_df_low = pd.read_excel(path, name)[['date', 'low']]
	lenlow = len(bond_cov_daily_df_low);
	bond_cov_daily_df_low.index = range(lenopen, lenopen + lenlow)
	bond_cov_daily_df_low = bond_cov_daily_df_low.rename(columns={'low': price})

	bond_cov_daily_df_high = pd.read_excel(path, name)[['date', 'high']]
	lenhigh = len(bond_cov_daily_df_high);
	bond_cov_daily_df_high.index = range(lenopen + lenlow, lenopen + lenlow + lenhigh)
	bond_cov_daily_df_high = bond_cov_daily_df_high.rename(columns={'high': price})

	bond_cov_daily_df_close = pd.read_excel(path, name)[['date', 'close']]
	lenclose = len(bond_cov_daily_df_close);
	bond_cov_daily_df_close.index = range(lenopen + lenlow + lenhigh, lenopen + lenlow + lenhigh + lenclose)
	bond_cov_daily_df_close = bond_cov_daily_df_close.rename(columns={'close': price})

	bond_cov_daily_df = pd.concat([bond_cov_daily_df_open, bond_cov_daily_df_low, bond_cov_daily_df_high, bond_cov_daily_df_close])
	return bond_cov_daily_df

def get_valanaly_df(path,name):
	bond_cov_valanaly_df = pd.read_excel(path, name)
	return bond_cov_valanaly_df


def select_interest_some(writer,bond_expect_df,tag):
		bond_expect_df = bond_expect_df.sort_values('下注比例', ascending=False)
		bond_expect_df.to_excel(writer, tag)
		optimaltag = 'opt-'+ tag;
		bond_expect_selected_df = bond_expect_df[(bond_expect_df['年均异动'] >= 3.0) & (bond_expect_df['下注比例'] >= 0.5) & (bond_expect_df['交易周期'] >= 1)]
		bond_expect_selected_df = bond_expect_selected_df.sort_values('交易周期', ascending=False)
		bond_expect_selected_df.to_excel(writer, optimaltag)

if __name__=='__main__':
		from sys import argv
		warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
		
		interestpath = ''
		today = datetime.datetime.now()
		if len(argv) > 2:
			if argv[2] == '*':
				today = datetime.datetime.now().strftime('%Y-%m-%d')
			else:
				today = datetime.datetime.strptime(argv[2], '%Y-%m-%d').strftime('%Y-%m-%d')
			print('**************computerday:%s*************' % today)
			
			interestpath = argv[1]
			isExist = os.path.exists(interestpath)
			if not isExist or 'selected' not in interestpath:
				print("please make sure the path:" + interestpath)
				exit(1)
		else:
			print("please run like 'python cartridge.py [file] [2022-08-22]'")
			exit(1)
		
			
		bond_interest_df = pd.read_excel(interestpath, 'clause')
		bond_kelly_df = pd.DataFrame(columns=['名称', '代码', '胜率', '赔率', '下注比例','纯债溢价率','当前价格','参考估价','保底涨幅','保底价格','00分位', '50分位', '100分位' ,'剩余规模','交易周期','年均异动','最后异动','异动阈值','异动涨幅','最后崩溃','崩溃阈值'])
		money = 'money'
		ratio = 'ratio'
		for i, bondrow in bond_interest_df.iterrows():
			name = bondrow['name'];
			bond = bondrow['code'];
			remain= bondrow['remain'];
			expval= bondrow['expval'];
			tradeyear = 6-bondrow['lastyear'];
			print('#########################名称:%s########################' % name)


			try:
				#the bond like '113546' not 'sh113546'
				numbond = bond[2:]
				valuepath,valuesheet = get_akshare_valanaly(numbond,today)
			except Exception as result:
				print(bond + " get bond error:" + str(result))
				continue
			print("get datapath ok:" + valuepath + ",sheetname:" +valuesheet)

			bond_cov_valanaly_df = get_valanaly_df(valuepath,valuesheet)
			#print(bond_cov_valanaly_df)
			totalcounts =  bond_cov_valanaly_df.shape[0]
			prerate = bond_cov_valanaly_df.loc[totalcounts-1]['纯债溢价率']
			datevalue  = bond_cov_valanaly_df.loc[totalcounts-1]['日期']
			pricevalue = bond_cov_valanaly_df.loc[totalcounts-1]['收盘价']
			wincounts = (bond_cov_valanaly_df[ bond_cov_valanaly_df['纯债溢价率'] > prerate ]).shape[0]
			print("totalcounts,wincounts,prerate,datevalue :",totalcounts,wincounts,prerate,datevalue)
			#胜率=成功总次数/(成功总次数+失败总次数)
			kellyp = wincounts / totalcounts
			
			dailysta = bond_cov_valanaly_df['收盘价'].describe()
			valuemin = dailysta['min'];valuemax = dailysta['max'];value50 = dailysta['50%']

			try:
				resultpath,insheetname = get_akshare_daily(bond,today)
			except Exception as result:
				print(bond + " get bond error:" + str(result))
				continue
			print("get datapath ok:" + resultpath + ",sheetname:" +insheetname)


			#异动指标
			try:
				bond_cov_collapse_df  = get_crash_dbscan_df(resultpath,insheetname)
				collapselatest = bond_cov_collapse_df.iloc[-1][0]
				collapseminvol = np.max(bond_cov_collapse_df['crash'])
				
				bond_cov_abnormal_df = get_abnormal_dbscan_df(resultpath,insheetname)
				cntguess,abnrate= guess_abnormal_parameter_additional(bond_cov_abnormal_df,tradeyear)
				valguess = pricevalue*(1+abnrate/100)	
				print("guess abnormal counts per year:%f,guess abnormal price:%f,guess abnormal rate per year:%f" % (cntguess,valguess,abnrate)) 
				
				#赔率2=各次异动条件下最大盈利中位数/失败时利息损失
				abnval = valguess
				kellyb1 = getkellybEx(pricevalue,expval,abnval,6-tradeyear) 
				print("abnormalhighmiddle:%f" % abnval)

				#250个交易日
				abnormalperyear = cntguess
				abnormallatest = bond_cov_abnormal_df.iloc[-1][0]
				abnormalminvol = np.min(bond_cov_abnormal_df['volume'])
				#print("--->"+str(abnormalminvol))
			except Exception as result:
				print("get abnormal error:" + bond)
				continue

			#下注比例
			kellyf1 = ((kellyb1+1)*kellyp-1)/kellyb1
			print("########胜率:%f,赔率:%f,下注比例:%f########" %(kellyp,kellyb1,kellyf1))
			
			exppercent = 100*(expval-pricevalue)/pricevalue
			
			bond_kelly_df = pd.concat([bond_kelly_df,pd.DataFrame({'名称':[name],'代码':[bond],'胜率':[kellyp],'赔率':[kellyb1],'下注比例':[kellyf1],'纯债溢价率':[prerate],
			'当前价格':[pricevalue],'参考估价':[abnval],'保底涨幅':[exppercent],'保底价格':[expval],'00分位':[valuemin],'50分位':[value50],'100分位':[valuemax],'剩余规模':[remain],'交易周期':[tradeyear],
			'年均异动':[abnormalperyear],'最后异动':[abnormallatest],'异动阈值':[abnormalminvol],'异动涨幅':[abnrate],
			'最后崩溃':[collapselatest],'崩溃阈值':[collapseminvol]})],ignore_index=True)


		#print(bond_kelly_df)

		fileout = today + '_kelly_bombs.xlsx'
		outanalypath = "%s/%s" % ('bond', fileout)
		writer = pd.ExcelWriter(outanalypath)
		#bond_kelly_df.to_excel(writer, 'kelly')
		select_interest_some(writer, bond_kelly_df, 'kelly')
		#writer.save()
		writer.close()
		print("kelly analy out path:" + outanalypath)






