import akshare as ak
import pandas as pd
from datetime import datetime
import os
import argparse
import requests
from typing import Optional
from akshare.utils import demjson

def bond_cb_index_jsl_with_cookie(cookie: Optional[str] = None) -> pd.DataFrame:
    """
    支持通过cookie获取集思录可转债等权指数数据
    """
    url = "https://www.jisilu.cn/webapi/cb/index_history/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
    }
    
    if cookie:
        headers["Cookie"] = cookie
    
    r = requests.get(url, headers=headers)
    data_dict = demjson.decode(r.text)["data"]  # type: ignore
    temp_df = pd.DataFrame(data_dict)
    return temp_df

# 解析命令行参数
parser = argparse.ArgumentParser(description='分析可转债等权指数连续下跌区间')
parser.add_argument('--days', type=int, default=5, help='连续下跌天数阈值，默认为5天')
parser.add_argument('--cookie', type=str, default=None, help='可选的cookie字符串，用于获取登录用户数据')
args = parser.parse_args()

# 生成数据文件名（不包含日期，用于存储所有历史数据）
filename = 'index_jsl_all.xlsx'

# 检查文件是否存在
if os.path.exists(filename):
    print(f"发现历史数据文件: {filename}，读取现有数据...")
    df_existing = pd.read_excel(filename)
    
    # 获取最新数据的日期
    latest_date = df_existing['price_dt'].max()
    print(f"现有数据最新日期: {latest_date}")
    
    # 获取新数据
    print("开始下载最新数据...")
    try:
        df_new = bond_cb_index_jsl_with_cookie(cookie=args.cookie)
    except Exception as e:
        print(f"下载最新数据失败: {e}，使用历史数据进行统计。")
        df = df_existing
    else:
        # 过滤出新数据（只保留比现有数据更新的部分）
        df_new_filtered = df_new[df_new['price_dt'] > latest_date]
        
        if not df_new_filtered.empty:
            print(f"发现 {len(df_new_filtered)} 条新数据，正在合并...")
            # 合并数据
            df = pd.concat([df_existing, df_new_filtered], ignore_index=True)
            # 保存合并后的数据
            df.to_excel(filename, index=False)
            print(f"数据已更新并保存到: {filename}")
        else:
            print("没有新数据，使用现有数据进行分析...")
            df = df_existing
else:
    print(f"未发现历史数据文件，开始下载完整数据...")
    # 获取可转债等权指数历史行情（集思录可转债等权指数）
    try:
        df = bond_cb_index_jsl_with_cookie(cookie=args.cookie)
    except Exception as e:
        print(f"下载完整数据失败: {e}，无法进行统计分析。")
        exit(1)
    # 保存为xlsx格式
    df.to_excel(filename, index=False)
    print(f"数据已保存到: {filename}")

# 确保按日期升序排列
if not df['price_dt'].is_monotonic_increasing:
    df = df.sort_values('price_dt').reset_index(drop=True)

# 计算每日涨跌（收盘价）
df['down'] = df['price'].diff() < 0

# 找出连续下跌区间
streaks = []
streak_start = None
streak_length = 0
for i, is_down in enumerate(df['down']):
    if is_down:
        if streak_start is None:
            streak_start = i
        streak_length += 1
    else:
        if streak_length >= args.days:
            streaks.append((df.loc[streak_start, 'price_dt'], df.loc[i-1, 'price_dt'], streak_length))
        streak_start = None
        streak_length = 0

# 检查结尾是否有未记录的下跌区间
if streak_length >= args.days:
    streaks.append((df.loc[streak_start, 'price_dt'], df.loc[len(df)-1, 'price_dt'], streak_length))

# 输出结果
if streaks:
    print(f"连续下跌{args.days}天及以上的区间:")
    for start, end, days in streaks:
        print(f"开始: {start}, 结束: {end}, 连续下跌: {days}天")
else:
    print(f"没有连续下跌{args.days}天及以上的区间。")