from .utils import *

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


def get_rtn_data(rtn):
    cumprod_rtn = (rtn + 1).cumprod() 
    cumprod_high = cumprod_rtn.cummax()

    cumsum_rtn = rtn.cumsum() + 1
    cumsum_high = cumsum_rtn.cummax()  # 단리면 수익률이 -1 밑으로 내려갈 가능성도 있지 않나..?

    cumprod_dd = cumprod_rtn / cumprod_high - 1
    cumsum_dd = cumsum_rtn / cumsum_high - 1
    
    cumprod_rtn -= 1
    cumsum_rtn -= 1
    
    df = pd.concat([cumprod_rtn, cumsum_rtn, cumprod_high, cumsum_high, cumprod_dd, cumsum_dd], axis=1)
    df.columns = ['cumprod_rtn', 'cumsum_rtn', 'cumprod_high', 'cumsum_high', 'cumprod_dd', 'cumsum_dd']
    return df


def show_cumprod_plot(strategy_rtn, benchmark_rtn=None):
    stg_rtn_data = get_rtn_data(strategy_rtn)

    fig, ax = plt.subplots(2, figsize = (15,8), gridspec_kw={'height_ratios': [2.5, 1], 'hspace':0.05}, sharex = True)

    if isinstance(benchmark_rtn, pd.Series):
        # 벤치마크 가격으로 볼지, 수익률로 볼지 생각해봐야함. 수익률로 보면 차이 많이날 시 의미 없음
        # 인덱스 맞추는 로직도 필요
        bchmk_rtn_data = get_rtn_data(benchmark_rtn)
        bchmk_rtn_data['cumprod_rtn'].plot(ax=ax[0], grid=True, label = 'KOSDAQ', legend = True, color = 'g')
        bchmk_rtn_data['cumprod_dd'].plot(ax=ax[1], grid=True, color = 'g');

    stg_rtn_data['cumprod_rtn'].plot(ax=ax[0], title = '누적 복리 수익률', grid=True, label = 'Strategy', legend = True, color = 'b');
    stg_rtn_data['cumprod_dd'].plot(ax=ax[1], grid=True, color = 'b');
    return None