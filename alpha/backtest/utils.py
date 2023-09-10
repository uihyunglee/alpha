import pandas as pd
import numpy as np
import requests
from io import BytesIO
from datetime import datetime as dt


def get_krx_content(otp_params):
    """krx crawling format: Return data corresponding to otp_params"""
    header = {"User-Agent": "Mozilla/5.0"}
    otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    otp = requests.post(otp_url, headers=header, data=otp_params).text
    
    down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
    down_params = {"code": otp}
    down_content = requests.post(down_url, headers=header, params=down_params).content

    df = pd.read_csv(BytesIO(down_content), encoding='EUC-KR')
    return df


def get_code2name_dict():
    """Return stock code-stock name from KRX (stocks currently listed)"""
    today = dt.now().strftime('%Y%m%d')
    otp_params = {
        "mktId": "ALL",
        "trdDd": today,
        "url": "dbms/MDC/STAT/standard/MDCSTAT01501"
    }
    df = get_krx_content(otp_params)
    code_to_company = pd.Series(index='A'+df['종목코드'], data=df['종목명'].values)
    return dict(code_to_company)


def get_index_info(index_name='KOSDAQ', start_date='20000101', end_date=dt.now().strftime('%Y%m%d'), only_close=True):
    """
    Return korea index information
    
    - index_name is 'KOSPI' or 'KOSPI200' or 'KOSDAQ' or 'KOSDAQ150'.
    - return dataframe with columns ['date', 'open', 'high', 'low', 'close', 'vol', 'trd_val', 'mc'].
    - if only_close is True, return close price series with date as index.
    """
    start_date = re.sub(r'[^0-9]', '', start_date)
    end_date = re.sub(r'[^0-9]', '', end_date)
    index_code = {
        "KOSPI":"1001",
        "KOSPI200": "1028",
        "KOSDAQ": "2001",
        "KOSDAQ150": "2203"
    }
    index_df = pd.DataFrame()
    while start_date < end_date:
        temp_start_date = str(int(end_date) - 10000)
        if temp_start_date < start_date:
            temp_start_date = start_date
            
        otp_params = {
            "indIdx": index_code[index_name][0],
            "indIdx2": index_code[index_name][1:],
            "strtDd": temp_start_date,
            "endDd": end_date,
            "url": "dbms/MDC/STAT/standard/MDCSTAT00301"
        }
        temp_df = get_krx_content(otp_params)
        index_df = pd.concat([index_df, temp_df], axis=0)
        end_date = str(int(temp_start_date) - 1)
        
    kor_col = ['일자', '시가', '고가', '저가', '종가', '거래량', '거래대금', '상장시가총액']
    eng_col = ['date', 'open', 'high', 'low', 'close', 'vol', 'trd_val', 'mc']
    index_df = index_df[kor_col].iloc[::-1,:]
    index_df.columns = eng_col
    index_df['date'] = pd.to_datetime(index_df['date'])
    index_df.set_index('date', drop=True, inplace=True)
    if only_close:
        return index_df['close']
    return index_df