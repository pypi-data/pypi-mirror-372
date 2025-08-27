# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
Date: 2025/3/26 21:15
Desc: 东方财富网-数据中心-股东分析
https://data.eastmoney.com/gdfx/
"""

import pandas as pd
import requests

def stock_hk_gdfx_top_10_em(
    symbol: str = "00300.HK", date: str = "20250630"
) -> pd.DataFrame:
    """
    东方财富网-港股个股-主要股东
    https://emweb.securities.eastmoney.com/PC_HKF10/pages/home/index.html?code=00144&type=web&color=w#/MajorShareholder
    :param symbol: 股票代码
    :type symbol: str
    :param date: 报告期
    :type date: str
    :return: 十大股东
    :rtype: pandas.DataFrame
    """
    url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"

    # 请求头（Headers）
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
        "Connection": "keep-alive",
        "Origin": "https://emweb.securities.eastmoney.com",
        "Referer": "https://emweb.securities.eastmoney.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }
    params = {
        "reportName": "RPT_HKF10_EQUITYCHG_HOLDER",
        "columns": "SECURITY_CODE,SECUCODE,ORG_CODE,NOTICE_DATE,REPORT_DATE,HOLDER_NAME,TOTAL_SHARES,TOTAL_SHARES_RATIO,DIRECT_SHARES,SHARES_CHG_RATIO,SHARES_TYPE,EQUITY_TYPE,HOLD_IDENTITY,IS_ZJ",
        "quoteColumns": "",
        "filter": f"(SECUCODE=\"{symbol}\")(REPORT_DATE='2025-03-31')",
        "pageNumber": "1",
        "pageSize": "",
        "sortTypes": "-1,-1",
        "sortColumns": "EQUITY_TYPE,TOTAL_SHARES",
        "source": "F10",
        "client": "PC",
        "v": f"04057334264822946"
    }
    r = requests.get(url, headers=headers, params=params)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["result"]["data"])
    temp_df.reset_index(inplace=True)
    temp_df["Index"] = temp_df.index + 1
    temp_df = temp_df.rename(columns={
        'Index':'名次',
        'HOLDER_NAME':'股东名称',
        'SHARES_TYPE':'股份类型',
        'TOTAL_SHARES':'持股数',
        'TOTAL_SHARES_RATIO':'占总股本持股比例',
        'SHARES_CHG_RATIO':'变动比率'
    })    
    return temp_df[['名次','股东名称','股份类型','持股数','占总股本持股比例','变动比率']]
