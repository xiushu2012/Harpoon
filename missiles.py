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
from pandas.core.common import SettingWithCopyWarning

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
	elif value >= v100:
		kellyb = (value - 1) / (value - v0)
	else:
		kellyb = (v100 - value) / (value - v0)
	print("kellyv0:%f,kellyv100:%f" % (v0,v100))
	return kellyb

def getkellybKx(value,expval,ltyear):
	# 赔率=获胜时的盈利/失败时的亏损(利息的损失)
	# 利息损失 = (value*(1+大额存单利率)**2 -value) - (value*(1+到期利率)**2 - value)
	deficit = value*(1+0.03)**ltyear - expval
	kellyb = 0.01
	if deficit <= 0:
		kellyb = (150-value)/1
	else:
		kellyb = (150-value)/deficit

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
	print("abnormal volumn:%d" % list(clusters).count(-1))
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
	bond_cov_abnormal_df['type'] = abnlier_det.fit_predict(bond_cov_abnormal_df[['ts']].values)
	#print(abnormal_df['type'])
	
	#print(bond_cov_volume_df)
	if not os.path.exists(path):
		bond_cov_abnormal_df.to_excel(writer, 'abnormal')
	else:
		with pd.ExcelWriter(path,engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
			bond_cov_abnormal_df.to_excel(writer, 'abnormal')	
	return bond_cov_abnormal_df


def guess_abnormal_parameter(abnormal_df):

	#strts0 = abnormal_df['date'].tolist()[0]
	#print('classify ' + strts0)
	#ts0 = time.mktime(time.strptime(str(strts0),"%Y-%m-%d %H:%M:%S"))  row['date']
	typedic = {}
	abnormal_high_df=abnormal_df[['high','type']]
	transtype = 0
	for i, abnrow in abnormal_high_df.iterrows():
			high = abnrow['high'];type = abnrow['type'];
			if type == -1:
				transtype = transtype - 1
				type = transtype
			
			if type in typedic.keys():
				typedic[type][0] =  typedic[type][0] + 1
				typedic[type][1] =  typedic[type][1] + high
			else:
				value=[]
				value.append(1);
				value.append(high)
				typedic[type]=value

	#print(typedic)
	
	type_df = pd.DataFrame(columns=['flag', 'avg'])
	for flag in typedic.keys():
			#print(flag)
			avg = typedic[flag][1]/typedic[flag][0]
			type_df = type_df.append({'flag':flag,'avg':avg},ignore_index=True)
	#print(type_df)
	avgsta = type_df['avg'].describe()
	return avgsta['count'],avgsta['50%']


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
		bond_expect_selected_df = bond_expect_df[(bond_expect_df['年均异动'] >= 2.0) & (bond_expect_df['下注比例'] >= 0.1) & (bond_expect_df['交易周期'] >= 1)]
		bond_expect_selected_df = bond_expect_selected_df.sort_values('保底涨幅', ascending=False)
		bond_expect_selected_df.to_excel(writer, optimaltag)
		
def get_price_kelly(value,expval,ltyear,delta,price):
		dvalue = value*(1-delta)
		dname = "价格%.3f" % (dvalue)
		dkellyb = getkellybKx(dvalue,expval,ltyear)
		dwincounts = price[ price > dvalue ].count()
		dkellyp = dwincounts / counts
		dkellyf = ((dkellyb+1)*dkellyp-1)/dkellyb
		print("预计价格%f,预计下注%f,胜率%f,赔率%f" % (dvalue,dkellyf,dkellyp,dkellyb))
		return dname,dkellyf


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
			if not isExist or 'braised' not in interestpath:
				print("please make sure the path:" + interestpath)
				exit(1)
		else:
			print("please run like 'python cartridge.py [file] [2022-08-22]'")
			exit(1)

		bond_interest_df = pd.read_excel(interestpath, 'clause')
		bond_kelly_df = pd.DataFrame(columns=['名称', '代码', '胜率', '赔率', '下注比例','跌幅1点','跌幅2点','跌幅3点','当前价格','保底涨幅','保底价格','异动涨幅','异动价格','75涨幅','剩余规模','交易周期','年均异动','最后异动','异动阈值'])
		money = 'money'
		ratio = 'ratio'
		for i, bondrow in bond_interest_df.iterrows():
			name = bondrow['name'];
			bond = bondrow['code'];
			remain= bondrow['remain'];
			expval= bondrow['expval'];
			ltyear = bondrow['lastyear'];
			print('#########################名称:%s########################' % name)
			try:
				resultpath,insheetname = get_akshare_daily(bond,today)
			except Exception as result:
				print(bond + " get bond error:" + str(result))
				continue
			print("get datapath ok:" + resultpath + ",sheetname:" +insheetname)


			bond_cov_daily_df = get_daily_df(resultpath, insheetname, money)
			dailysta = bond_cov_daily_df[money].describe()
			bond_cov_biginc_df = get_dailyinc_df(resultpath, insheetname,ratio)
			incsta = bond_cov_biginc_df[ratio].describe()
			inc75 = incsta['75%']

			counts = dailysta['count']
			tradeyears  =  counts/4/250

			date = bond_cov_daily_df.loc[counts-1][0]
			value = bond_cov_daily_df.loc[counts-1][1]

			valuemin = dailysta['min'];valuemax = dailysta['max']
			value25 = dailysta['25%'];value50 = dailysta['50%'];value75 = dailysta['75%']

			price =  bond_cov_daily_df[money]
			wincounts = price[ price > value ].count()
			#成功总次数/(成功总次数+失败总次数)
			kellyp = wincounts / counts



			#异动指标
			try:
				bond_cov_abnormal_df = get_abnormal_dbscan_df(resultpath,insheetname)
				cntguess,valguess= guess_abnormal_parameter(bond_cov_abnormal_df)
				print("guess abnormal counts:%f,guess abnormal avg:%f" % (cntguess,valguess)) 
				
				#赔率2=各次异动条件下最大盈利中位数/失败时的最大亏损

				kellyb = getkellybKx(value,expval,ltyear)
				
				abnval = valguess;abnormalcount = cntguess
				print("abnormalhighmiddle:%f" % abnval)
				#print("abnormalcount:%d" % abnormalcount)
				
				#250个交易日
				abnormalperyear = abnormalcount/tradeyears
				abnormallatest = bond_cov_abnormal_df.iloc[-1][0]
				abnormalminvol = np.min(bond_cov_abnormal_df['volume'])
				#print("--->"+str(abnormalminvol))
			except Exception as result:
				print("get abnormal error:" + bond)
				continue

			#下注比例
			kellyf = ((kellyb+1)*kellyp-1)/kellyb
			print("########胜率:%f,赔率:%f,下注比例:%f########" %(kellyp,kellyb,kellyf))
			
			exppercent = 100*(expval-value)/value
			abnpercent = 100*(abnval-value)/value
			
			

			valname01,kellyf01 = get_price_kelly(value,expval,ltyear,0.01,price)
			valname02,kellyf02 = get_price_kelly(value,expval,ltyear,0.02,price)
			valname03,kellyf03 = get_price_kelly(value,expval,ltyear,0.03,price)

			bond_kelly_df = bond_kelly_df.append({'名称':name,'代码':bond,'胜率':kellyp,'赔率':kellyb,
			'下注比例':kellyf,'跌幅1点':kellyf01,'跌幅2点':kellyf02,'跌幅3点':kellyf03,
			'当前价格':value,'保底涨幅':exppercent,'保底价格':expval,'异动涨幅':abnpercent,'异动价格':abnval,'75涨幅':inc75,
			'剩余规模':remain,'交易周期':tradeyears,'年均异动':abnormalperyear,'最后异动':abnormallatest,'异动阈值':abnormalminvol},ignore_index=True)


		#print(bond_kelly_df)

		fileout = today + '_kelly_missiles.xlsx'
		outanalypath = "%s/%s" % ('bond', fileout)
		writer = pd.ExcelWriter(outanalypath)
		#bond_kelly_df.to_excel(writer, 'kelly')
		select_interest_some(writer, bond_kelly_df, 'kelly')
		writer.save()
		print("kelly analy out path:" + outanalypath)






