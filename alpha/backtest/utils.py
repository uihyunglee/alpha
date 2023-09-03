import pandas as pd
import numpy as np
import requests
from io import BytesIO


def get_krx_content(self, otp_params):
    """krx crawling format: Return data corresponding to otp_params"""
    otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    otp = requests.post(otp_url, headers=self.header, data=otp_params).text
    
    down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
    down_params = {"code": otp}
    down_content = requests.post(down_url, headers=self.header, params=down_params).content

    df = pd.read_csv(BytesIO(down_content), encoding='EUC-KR')
    return df


def krx_code():
    url = 'https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
    krx = pd.read_html(url, header=0)[0]
    krx['종목코드'] = krx['종목코드'].map('A{:06d}'.format).values
    krx.index = krx.pop('종목코드')
    krx_codename = krx['회사명']
    return krx_codename


def condition_statistic(self, condition):
    condition.sum().plot(figsize = (10,5), title = '일별 시그널 발생 횟수');
    print(condition.sum().describe())
    
