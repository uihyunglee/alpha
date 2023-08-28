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