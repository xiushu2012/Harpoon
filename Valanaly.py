# -*- coding: utf-8 -*-

import akshare as ak
import numpy as np  
import pandas as pd  
import math
import datetime
import os
import matplotlib.pyplot as plt
import openpyxl

def get_akshare_valanaly(xlsfile,stock):
	shname='daily'
	isExist = os.path.exists(xlsfile)
	if not isExist:
		#bond_zh_hs_cov_daily_df = ak.bond_zh_hs_cov_daily(symbol=stock)
		#bond_zh_hs_cov_daily_df.to_excel(xlsfile,sheet_name=shname)
		
		bond_zh_cov_value_analysis_df = ak.bond_zh_cov_value_analysis(symbol=stock)
		bond_zh_cov_value_analysis_df.to_excel(xlsfile,sheet_name=shname)
		
		print("xfsfile:%s create" % (xlsfile))  
	else:
		print("xfsfile:%s exist" % (xlsfile))
	
	return xlsfile,shname


if __name__=='__main__':

		from sys import argv
		stock = ''
		if len(argv) > 1:
				stock = argv[1]
		else:
				print("please run like 'python Valanaly.py [113527]'")
				exit(1)
		dailypath =  "./%s.xls" % (stock)
		resultpath,insheetname = get_akshare_valanaly(dailypath,stock)
		print("data of path:" + resultpath + ",sheetname:" +insheetname)





