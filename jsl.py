# -*- coding: utf-8 -*-

import akshare as ak
import numpy as np  
import pandas as pd  
import math
import datetime
import os
import matplotlib.pyplot as plt
import openpyxl

def get_akshare_jsl(xlsfile,cookie):
	shname='jsl'
	isExist = os.path.exists(xlsfile)
	if not isExist:
		bond_convert_jsl_df = ak.bond_cb_jsl(cookie)
		bond_convert_jsl_df.to_excel(xlsfile,sheet_name=shname)
		
		print("xfsfile:%s create" % (xlsfile))  
	else:
		print("xfsfile:%s exist" % (xlsfile))
	
	return xlsfile,shname


if __name__=='__main__':
		from sys import argv
		cookie = ""
		if len(argv) > 1:
			cookie = argv[1]
		else:
			print("please run like 'python jsl.py cookie'")
			print("1.F12或者单击鼠标右键，选择审查元素")
			print("2.点击Console,输入指令 document.cookie,回车即可显示当前页面cookie信息")
			exit(1)

		jslpath =  "./%s.xls" % ('jsl')
		resultpath,insheetname = get_akshare_jsl(jslpath,cookie)
		print("data of path:" + resultpath + ",sheetname:" +insheetname)





