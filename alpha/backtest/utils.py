import pandas as pd
import numpy as np

def krx_code():
    url = 'https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
    krx = pd.read_html(url, header=0)[0]
    krx['종목코드'] = krx['종목코드'].map('A{:06d}'.format).values
    krx.index = krx.pop('종목코드')
    krx_codename = krx['회사명']
    return krx_codename