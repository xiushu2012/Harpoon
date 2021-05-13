
# -*- coding: utf-8 -*-

import akshare as ak
import numpy as np  
import pandas as pd  
import math
import datetime
import time
import os
import matplotlib.pyplot as plt
import openpyxl
from sys import argv



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
def calc_bond_gains(bond_daily_df,floor,roof,price):

	print("premium-floor-roof  :", floor, roof)
	datetoday = bond_daily_df.iloc[-1]['date']
	premtoday = bond_daily_df.iloc[-1]['premium']
	pircetoday = bond_daily_df.iloc[-1][price]

	bond_daily_low =  bond_daily_df[bond_daily_df['premium'] < floor]
	bond_daily_high = bond_daily_df[bond_daily_df['premium'] > roof]

	total = 1.0;peryear=0.0
	datepos = bond_daily_low.iloc[0]['date']

	for i, lowrow in bond_daily_low.iterrows():
		datelow = lowrow['date']
		if(datelow >= datepos):
			bond_filter_df = bond_daily_high[bond_daily_high['date'] > datelow]
			if bond_filter_df.empty:
				break
			else:
				highrow = bond_filter_df.iloc[0]
				growth = (highrow[price]- lowrow[price])/lowrow[price]
				total =  total * (growth + 1)
				datepos = highrow['date']
				print(lowrow['date'],lowrow[price],lowrow['premium'])
				print(highrow['date'], highrow[price], highrow['premium'])

	gaindays = (bond_daily_df.iloc[-1]['date'] - bond_daily_df.iloc[0]['date']).days
	peryear =  np.e**(np.log(total)/(gaindays/365)) - 1
	return total,peryear,datetoday,premtoday,pircetoday


def calc_bond_overflow(price,bondvalue):
	return 100 * (price - bondvalue) / bondvalue

def calc_bond_value(date,price,yeardf):
	yearresdf = yeardf[ yeardf['year'] > date ]

	totaldiscounts = 0.0;calyears = 0
	for i, yearrow in yearresdf.iterrows():
		calyears = calyears +  1
		curdiscounts = yearrow['val']/(1+0.04)**calyears
		totaldiscounts = curdiscounts + totaldiscounts

	captialdiscounts = 100 / (1 + 0.04) ** calyears
	totaldiscounts = captialdiscounts + totaldiscounts

	#print(date,price,totaldiscounts)
	return totaldiscounts


def calc_return_year(lastdate,rt1,rt2,rt3,rt4,rt5,rt6):
	year6 = lastdate
	year5 = year6 - pd.Timedelta(days=365)
	year4 = year6 - pd.Timedelta(days=365 * 2)
	year3 = year6 - pd.Timedelta(days=365 * 3)
	year2 = year6 - pd.Timedelta(days=365 * 4)
	year1 = year6 - pd.Timedelta(days=365 * 5)

	yeardic = {'year': [year1,year2,year3,year4,year5,year6],
			    'val': [rt1,  rt2,  rt3,  rt4,  rt5,  rt6]}
	yeardf =  pd.DataFrame(yeardic)
	return yeardf


if __name__=='__main__':
		interestpath = "./interest.xls"
		isExist = os.path.exists(interestpath)
		if not isExist:
			print("please make sure the ./interest.xls")
			exit(1)

		price = 'open'
		if len(argv) > 1:
			price = argv[1]
			print("computer price is:",price)
		else:
			print("computer price is: 'open'")


		bond_interest_df = pd.read_excel(interestpath, 'clause')
		bond_welfare_df = pd.DataFrame(columns=['name','totalgains','pergains','floor','roof','datetoday','premtoday','pircetoday'])
		for i, bondrow in bond_interest_df.iterrows():
			name = bondrow['name'];code = bondrow['code'];lastdate = bondrow['maturity']
			year_return_df = calc_return_year(lastdate, bondrow['rt1'], bondrow['rt2'], bondrow['rt3'],bondrow['rt4'], bondrow['rt5'], bondrow['rt6'])

			dailypath =  "./bond/%s.xls" % (code)
			resultpath,insheetname = get_akshare_daily(dailypath,code)

			print("data of path:" + resultpath + ",sheetname:" +insheetname)

			bond_cov_daily_df = pd.read_excel(resultpath, insheetname)[['date', price]]
			bond_cov_daily_df['value'] =   bond_cov_daily_df.apply(lambda row: calc_bond_value(row['date'], row[price], year_return_df), axis=1)
			bond_cov_daily_df['premium'] = bond_cov_daily_df.apply(lambda row: calc_bond_overflow(row[price], row['value']),axis=1)

			dailysta = bond_cov_daily_df['premium'].describe()
			value25 = dailysta['25%'];value50 = dailysta['50%'];value75 = dailysta['75%']
			print("value25-value50-value75:",value25,value50,value75)

			total50,peryear50,datetoday,premtoday,pircetoday = calc_bond_gains(bond_cov_daily_df,value25,value50,price)
			bond_welfare_df = bond_welfare_df.append({'name':name,'totalgains':total50,'pergains':peryear50,'floor':value25,'roof':value50,'datetoday':datetoday,'premtoday':premtoday,'pircetoday':pircetoday},ignore_index=True)

			total75,peryear75,datetoday,premtoday,pircetoday= calc_bond_gains(bond_cov_daily_df, value25, value75,price)
			bond_welfare_df = bond_welfare_df.append({'name':name,'totalgains':total75,'pergains': peryear75,'floor':value25,'roof':value75,'datetoday':datetoday,'premtoday':premtoday,'pircetoday':pircetoday},ignore_index=True)
			print("###############################################")
		print(bond_welfare_df)
		tnow = datetime.datetime.now()
		fileout = tnow.strftime('%Y_%m_%d') +'_' + price +'_welfare.xls'
		outanalypath = "%s/%s" % ('bond', fileout)
		writer = pd.ExcelWriter(outanalypath)
		bond_welfare_df.to_excel(writer, 'welfare')
		writer.save()
		print("History analy out path:" + outanalypath)






