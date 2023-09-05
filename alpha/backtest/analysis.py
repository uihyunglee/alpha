from .utils import *

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


def get_rtn_data(rtn):
    """Return cumulative prod and sum return and drawdown"""
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


def show_rtn_plot(strategy_rtn, benchmark_rtn=None, benchmark_price=None, func='cumprod'):
    """Show cumulative return of strategy, benchmark and benchmark price"""
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
    
    title = '복리' if func=='cumprod' else '단리'
    stg_rtn_data[f'{func}_rtn'].plot(ax=ax[0], title = f'누적 {title} 수익률', grid=True, label = 'Strategy', legend = True, color = 'b');
    stg_rtn_data[f'{func}_dd'].plot(ax=ax[1], grid=True, color = 'b');
    return None


def show_rtn_analysis(strategy_rtn, benchmark_rtn=None, benchmark_price=False):
    """Show total return analysis information (input daily return)"""
    strategy_rtn = strategy_rtn.copy()
    strategy_rtn = strategy_rtn.fillna(0)
    
    tot_days = strategy_rtn.index[-1] - strategy_rtn.index[0]
    tot_days = tot_days.days
    tot_op_days = strategy_rtn.resample('D').size().shape[0]
    tot_yrs = tot_days / 365
    
    stg_rtn_data = get_rtn_data(strategy_rtn)
    rtn_avg = strategy_rtn.mean()
    rtn_std = strategy_rtn.std()  # 보수적 수치
    sharpe = rtn_avg / rtn_std * np.sqrt(252)  # 코인의 경우 기간 조정 필요
    sortino = rtn_avg / np.sqrt((strategy_rtn[strategy_rtn < 0] ** 2).sum() / len(strategy_rtn)) * np.sqrt(252)
    
    win_rate = (strategy_rtn > 0).sum() / strategy_rtn.shape[0]
    win_avg_rtn = strategy_rtn[strategy_rtn > 0].mean()
    lose_avg_rtn = strategy_rtn[strategy_rtn < 0].mean()

    print('-'*50)
    print(f'백테스트 기간: {strategy_rtn.index[0]} ~ {strategy_rtn.index[-1]}')
    print(f"- 총 캘린더: {tot_days}일")
    print(f"- 총 거래일: {tot_op_days}일")
    print(f"- 총 연도: {tot_yrs:.2f}년")
    print()
    print(f"전체 기간 복리 수익률: {stg_rtn_data['cumprod_rtn'].iloc[-1]:.2%}")
    print(f"전체 기간 단리 수익률: {stg_rtn_data['cumsum_rtn'].iloc[-1]:.2%}")
    print(f"복리 최대 낙폭(MDD): {stg_rtn_data['cumprod_dd'].min():.2%}")
    print(f"단리 최대 낙폭(MDD): {stg_rtn_data['cumsum_dd'].min():.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Sortino Ratio: {sortino:.2f}")
    print()
    print(f"연평균 복리 수익률: {(stg_rtn_data['cumprod_rtn'].iloc[-1] + 1)**(1 / tot_yrs) - 1:.2%}")
    print(f"연평균 단리 수익률: {stg_rtn_data['cumsum_rtn'].iloc[-1] / tot_yrs:.2%}")
    print(f"연평균 표준편차: {rtn_std * np.sqrt(252):.4}")
    print()
    print(f"일별 승률: {win_rate:.2%}")
    print(f"일별 평균 수익률: {rtn_avg: .2%}")
    print(f"일별 수익거래 수익률: {win_avg_rtn:.2%}")
    print(f"일별 손실거래 손실률: {lose_avg_rtn:.2%}")
    print(f"일별 손익비: {win_rate * (1 + win_avg_rtn / abs(lose_avg_rtn)):.2f}")
    print('-'*50)
    
    show_rtn_plot(strategy_rtn, benchmark_rtn, benchmark_price, func='cumprod')
    show_rtn_plot(strategy_rtn, benchmark_rtn, benchmark_price, func='cumsum')
    return None