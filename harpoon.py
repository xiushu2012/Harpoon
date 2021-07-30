# -*- coding: utf-8 -*-

import akshare as ak
import numpy as np  
import pandas as pd  
import math
import datetime
import os
import matplotlib.pyplot as plt
import openpyxl

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.width',1000)


def get_akshare_jsl(xlsfile):
    shname = 'jsl'
    isExist = os.path.exists(xlsfile)
    if not isExist:
        bond_convert_jsl_df = ak.bond_cov_jsl('kbzw__Session=hmsotphrfs3vin1iuboboik554; Hm_lvt_164fe01b1433a19b507595a43bf58262=1627631392; kbz_newcookie=1; kbzw_r_uname=weavernet; kbzw__user_login=7Obd08_P1ebax9aX7sfX19zp4d3VkZyh6dbc7OPm1Nq_1KLVr5XSltaw2qHbn67E2ZTZraPeltWSrLCnz9vN2pStkZiyoO3K1L_RpK2ZrZ-qk5ecpMy01r6bruPz3tXlzaaXpJGXn8rhz9TQ6-yVt82MqJKkkbKXyuHPppWvme2frZWXo-bR49zK3cO7yuioqpywmqqYlonCv8fFrZyB4OLgzpmz3MXh0KCXtuDT387ZqK6Zp5yllqqUp6WlqZOQtNXf1tvim6yVrY-qrQ..; Hm_lpvt_164fe01b1433a19b507595a43bf58262=1627631428')
        bond_convert_jsl_df.to_excel(xlsfile, sheet_name=shname)

        print("xfsfile:%s create" % (xlsfile))
    else:
        print("xfsfile:%s exist" % (xlsfile))

    return xlsfile, shname

def calc_value_center():
	stock_premium = [0.81,0,-0.1,-5.56,-3,8.34,0.28,-5.2,-8.24,2.34,-7.3,-26.52,-0.29]
	debt_premium =  [-2.79,0.79,2.09,2.58,2.89,4.63,5.18,7.33,7.4,7.44,7.46,9.23,9.52]
	return np.mean(stock_premium),np.mean(debt_premium)


def calc_value_distance(a, b,va,vb):
	return math.sqrt((a-va)**2+(b-vb)**2)

def calc_bond_value(price,ratio,year):
    if ratio == '-':
        return 130
    else:
        ratio = float(ratio.strip('%'))/100
        govload = 0.04
        return price*(1+ratio)**year/(1+govload)**year

def calc_bond_overflow(price,bondvalue):
    return 100 * (price - bondvalue) / bondvalue

def calc_stock_overflow(overflow):
    return float(overflow.strip('%'))


def get_pass_days(date):
	if date == '-':
		return -99
	else:
		delt = datetime.datetime.now() - datetime.datetime.strptime(date, '%Y%m%d')
		return delt.days


if __name__=='__main__':

    from sys import argv
    tnow = ""
    if len(argv) > 1:
        if argv[1] == '*':
            tnow = datetime.datetime.now()
        else:
            tnow = datetime.datetime.strptime(argv[1], '%Y/%m/%d')
    else:
        print("please run like 'python harpoon.py [*|2020/07/07]'")
        exit(1)

    print("time is :" + tnow.strftime('%Y%m%d'))

    filefolder = r'./data/' + tnow.strftime('%Y%m%d')
    filein = tnow.strftime('%Y_%m_%d') + '_in.xls'
    getakpath =  "%s/%s" % (filefolder,filein)

    isExist = os.path.exists(filefolder)
    if not isExist:
        os.makedirs(filefolder)
        print("AkShareFile:%s create" % (filefolder))
    else:
        print("AkShareFile:%s exist" % (filefolder))

    resultpath,insheetname = get_akshare_jsl(getakpath)
    print("data of path:" + resultpath + "sheetname:" +insheetname)


    va,vb = calc_value_center()
    print("the average of unlisted bond 转股溢价率,纯债溢价率",va,vb)


    bond_cov_jsl_df = pd.read_excel(resultpath, insheetname,converters={'stock_cd':str})[['bond_nm', 'stock_cd','orig_iss_amt','rating_cd','guarantor','price','year_left','ytm_rt','convert_value','premium_rt','force_redeem','convert_cd_tip','adj_cnt','adj_scnt','pre_bond_id']]
    bond_cov_jsl_df.rename(columns={'bond_nm': '转债名称', 'stock_cd': '正股代码','orig_iss_amt':'发行规模','rating_cd':'评级','guarantor':'担保情况','price':'最新价','year_left':'剩余期限','ytm_rt':'到期年化','convert_value':'转股价值','premium_rt':'转股溢价率','force_redeem':'强赎公告','convert_cd_tip':'转股提示','adj_cnt':'下修次数','adj_scnt':'成功次数','pre_bond_id':'转债代码'}, inplace=True)

    bond_cov_jsl_df['纯债价值'] = bond_cov_jsl_df.apply(lambda row: calc_bond_value(row['最新价'],row['到期年化'],row['剩余期限']), axis=1)
    bond_cov_jsl_df['纯债溢价率'] = bond_cov_jsl_df.apply(lambda row: calc_bond_overflow(row['最新价'],row['纯债价值']), axis=1)
    bond_cov_jsl_df['转股溢价率'] = bond_cov_jsl_df.apply(lambda row: calc_stock_overflow(row['转股溢价率']), axis=1)

    bond_cov_jsl_df['估值距离'] = bond_cov_jsl_df.apply(lambda row: calc_value_distance(row['转股溢价率'], row['纯债溢价率'],va,vb), axis=1)
    #bond_expect_sort_df = bond_cov_jsl_df.sort_values('估值距离',ascending=True)
    bond_expect_sort_df = bond_cov_jsl_df.sort_values('发行规模', ascending=True)
    bond_expect_sort_df = bond_expect_sort_df[['转债代码','转债名称','正股代码','到期年化','转股价值','转股溢价率','纯债价值','纯债溢价率','估值距离','最新价','发行规模','评级','担保情况','剩余期限','转股提示','下修次数','成功次数','强赎公告']]

    bond_expect_startup_df = bond_expect_sort_df[bond_expect_sort_df['正股代码'].str.contains(r'^3.*?')]
    bond_expect_smallboard_df = bond_expect_sort_df[bond_expect_sort_df['正股代码'].str.contains(r'^0.*?')]
    bond_expect_bigboard_df = bond_expect_sort_df[bond_expect_sort_df['正股代码'].str.contains(r'^6.*?')]

    #bond_expect_selected_df = bond_expect_sort_df[bond_expect_sort_df['发行规模'] <= 4.0 & bond_expect_sort_df['最新价'] <= 110.0 & bond_expect_sort_df['估值距离'] <= 20.0]
    bond_expect_selected_df = bond_expect_startup_df[(bond_expect_startup_df['发行规模'] <= 7.0)  & (bond_expect_startup_df['最新价'] <= 120.0)]
    bond_expect_selected_df = bond_expect_selected_df.sort_values('估值距离',ascending=True)
    
    bond_expect_candidate_df = bond_expect_smallboard_df[(bond_expect_smallboard_df['发行规模'] <= 7.0)  & (bond_expect_smallboard_df['最新价'] <= 120.0)]
    bond_expect_candidate_df = bond_expect_candidate_df.sort_values('估值距离',ascending=True)

    bond_expect_alternate_df = bond_expect_bigboard_df[(bond_expect_bigboard_df['发行规模'] <= 7.0)  & (bond_expect_bigboard_df['最新价'] <= 120.0)]
    bond_expect_alternate_df = bond_expect_alternate_df.sort_values('估值距离',ascending=True)

    fileout = tnow.strftime('%Y_%m_%d') + '_out.xls'
    outanalypath =  "%s/%s" % (filefolder,fileout)
    writer = pd.ExcelWriter(outanalypath)
    bond_expect_sort_df.to_excel(writer,'analyze')
    bond_expect_startup_df.to_excel(writer,'startup')
    bond_expect_smallboard_df.to_excel(writer,'smallboard')
    bond_expect_bigboard_df.to_excel(writer,'bigboard')
    bond_expect_selected_df.to_excel(writer,'selected')
    bond_expect_candidate_df.to_excel(writer,'candidate')
    bond_expect_alternate_df.to_excel(writer,'alternate')
    writer.save()
    print("value distance of  'unlist and analye' :" + fileout)


    #print(bond_expect_sort_df)
    # 显示散点图
    #bond_expect_sort_df.plot.scatter(x='纯债溢价率', y='转股溢价率')
    X = bond_expect_sort_df.values
    #plt.plot(X[:,6], X[:,4],"ro")
    txt = X[:,1].reshape(1, -1)[0]
    x = X[:,7].reshape(1, -1)[0]
    y = X[:,5].reshape(1, -1)[0]
    plt.scatter(x,y)
    for i in range(len(txt)):
        plt.annotate(txt[i][0:2], xy = (x[i],y[i]), xytext = (x[i]+0.1, y[i]+0.1)) #这里xy是需要标记的坐标，xytext是对应的标签坐标


    # 显示图
    plt.xlabel('纯债溢价率')
    plt.ylabel('转股溢价率')
    plt.rcParams['font.sans-serif']=['SimHei']

    fileimage = tnow.strftime('%Y_%m_%d') + '_image.png'
    imagepath =  "%s/%s" % (filefolder,fileimage)
    plt.savefig(imagepath)
    print("value image of  path:" + imagepath )
    #plt.show()




#对pandas中的Series和Dataframe进行排序，主要使用sort_values()和sort_index()。
#DataFrame.sort_values(by, axis=0, ascending=True, inplace=False, kind=‘quicksort’, na_position=‘last’)
#by：列名，按照某列排序
#axis：按照index排序还是按照column排序
#ascending：是否升序排列
#kind：选择 排序算法{‘quicksort’, ‘mergesort’, ‘heapsort’}, 默认是‘quicksort’，也就是快排
#na_position：nan排列的位置，是前还是后{‘first’, ‘last’}, 默认是‘last’
#sort_index() 的参数和上面差不多。





