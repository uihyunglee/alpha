import pandas as pd


def get_market_timing_cond(mk_price, df_format, ma=[3,5,10]):
    mt_cond = pd.Series().reindex_like(mk_price)
    for n in ma:
        market_ma = mk_price.rolling(n).mean()
        mt_cond = mk_price < market_ma
        sell_condition &= mt_cond
    start, end = df_format.columns[0], df_format.columns[-1]
    mt_cond_df = pd.DataFrame().reindex_like(df_format)
    mt_cond_df.iloc[0,:] = sell_condition.loc[start:end]
    mt_cond_df.fillna(method='ffill', axis=0, inplace = True)
    return mt_cond_df
