# -*- coding: utf-8 -*-
	
import pandas as pd
from selenium import webdriver
import time
import json
import datetime
import os

def get_browser(url):
    options = webdriver.ChromeOptions()
    #options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)


    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                          get: () => undefined
                        })
                      """
    })
    
    get_cookie(driver,url)
    set_cookie(driver)
    
    return driver



def set_cookie(driver):
	with open('cookies.json', 'r', encoding='utf-8') as f:
		listCookies = json.loads(f.read())

	for cookie in listCookies:
		driver.add_cookie(cookie)


def get_cookie(driver,url):
	driver.get(url)
	#这里可以手动登录 或者代码登录 
	time.sleep(50)
	dictCookies = driver.get_cookies()
	jsonCookies = json.dumps(dictCookies)
	print(jsonCookies)
	# 登录完成后，将cookie保存到本地文件
	with open('cookies.json', 'w') as f:
		f.write(jsonCookies)
	print("please check cookie in cookies.json")

def convert_float(rt1,rt2):
		ratio1 = float(rt1.strip('%'))
		ratio2 = float(rt2.strip('%'))
		return ratio1,ratio2


if __name__=='__main__':
			url = 'https://www.jisilu.cn/data/cbnew/#cb'
			browser = get_browser(url)
						
			browser.get(url)
			time.sleep(15)
			data = browser.page_source
						
			tables = pd.read_html(data,header=1)
			jsl_df = tables[0]
			
			
			tnow = datetime.datetime.now()
			print("time is :" + tnow.strftime('%Y%m%d'))
			filefolder = r'./data/' + tnow.strftime('%Y%m%d')
			filein = tnow.strftime('%Y_%m_%d') + '_in.xlsx'
			getakpath =  "%s/%s" % (filefolder,filein)
			isExist = os.path.exists(filefolder)
			
			if not isExist:
				os.makedirs(filefolder)
				print("creeepjsl :%s create" % (filefolder))
			else:
				print("creeepjsl:%s exist" % (filefolder))
				
			jsl_df.replace('-','0',inplace=True)
			jsl_df=jsl_df[['转债名称', '正股名称','剩余规模(亿元)','债券评级','现 价','剩余年限','到期税前收益','转股价值','转股溢价率','代 码']]
			jsl_df[['到期税前收益','转股溢价率']]=jsl_df[['到期税前收益','转股溢价率']].apply(lambda row: convert_float(row['到期税前收益'],row['转股溢价率']), axis=1,result_type="expand")
			jsl_df.rename(columns={'转债名称': '转债名称', '正股名称': '正股名称','剩余规模(亿元)':'剩余规模','债券评级':'评级','现 价':'现价','剩余年限':'剩余年限','到期税前收益':'到期税前收益','转股价值':'转股价值','转股溢价率':'转股溢价率','代 码':'代码'}, inplace=True)
			#jsl_df = jsl_df.append({'force_redeem':'','adj_scnt':'','adj_cnt':'','guarantor':'','convert_cd_tip':''},ignore_index=True)

			
			jsl_df.to_excel(getakpath,index=False,sheet_name='jsl')
			print("data of path:" + getakpath)