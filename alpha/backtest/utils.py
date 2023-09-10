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
