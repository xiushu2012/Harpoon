# -*- coding: utf-8 -*-

import akshare as ak
import numpy as np  
import pandas as pd  
import math
import datetime
import os
import matplotlib.pyplot as plt
import openpyxl

def get_akshare_jsl(xlsfile):
	shname='jsl'
	isExist = os.path.exists(xlsfile)
	if not isExist:
		bond_convert_jsl_df = ak.bond_cov_jsl()
		bond_convert_jsl_df.to_excel(xlsfile,sheet_name=shname)
		
		print("xfsfile:%s create" % (xlsfile))  
	else:
		print("xfsfile:%s exist" % (xlsfile))
	
	return xlsfile,shname


if __name__=='__main__':

		jslpath =  "./%s.xls" % ('jsl')
		resultpath,insheetname = get_akshare_jsl(jslpath)
		print("data of path:" + resultpath + ",sheetname:" +insheetname)





