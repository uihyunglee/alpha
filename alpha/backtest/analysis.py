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


def show_rtn_plot(strategy_rtn, benchmark_rtn=None, benchmark_price=False, func='cumprod'):
    stg_rtn_data = get_rtn_data(strategy_rtn)

    fig, ax = plt.subplots(2, figsize = (15,8), gridspec_kw={'height_ratios': [2.5, 1], 'hspace':0.05}, sharex = True)
    
    if isinstance(benchmark_price, pd.Series):
        benchmark_price.plot(ax=ax[0], grid=True, label = 'Price', legend = True, color = 'black', alpha=0.5, secondary_y=True)
        benchmark_price_high = benchmark_price.cummax()
        benchmark_price_dd = benchmark_price / benchmark_price_high - 1
        benchmark_price_dd.plot(ax=ax[1], grid=True, color = 'black', alpha=0.5);

    if isinstance(benchmark_rtn, pd.Series):
        bchmk_rtn_data = get_rtn_data(benchmark_rtn)
        bchmk_rtn_data[f'{func}_rtn'].plot(ax=ax[0], grid=True, label = 'Benchmark', legend = True, color = 'g', alpha=0.7)
        bchmk_rtn_data[f'{func}_dd'].plot(ax=ax[1], grid=True, color = 'g', alpha=0.7);

    stg_rtn_data[f'{func}_rtn'].plot(ax=ax[0], title = '누적 복리 수익률', grid=True, label = 'Strategy', legend = True, color = 'b');
    stg_rtn_data[f'{func}dd'].plot(ax=ax[1], grid=True, color = 'b');
    return None