import pandas as pd
import psycopg2
import json
import re

class AlphaDB:
    def __init__(self, info_path):
        """
        This class requires 'info_path'.
        ex) 'C:/Users/Desktop/info.json'
        
        json format: {"host":***, "user":***, "password":***, "dbname":***, "port":***}
        """
        with open(info_path, "r") as info:
            connect_info = json.load(info)

        self.conn = psycopg2.connect(**connect_info)
        
    def get_table_names(self):
        """Return DB table name"""
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        table_name = pd.read_sql(sql, self.conn)
        return list(table_name.values.reshape(-1))
        
    def get_stock_data(self, table, code=None, start_date=None, end_date=None, only_stock=False, only_ohlcv=False):
        """Return stock data in table"""
        if start_date == None:
            start_date = '0'
        if end_date == None:
            end_date = '3000_00_00'
        start_date = int(re.sub(r'[^0-9]', '', start_date))
        end_date = int(re.sub(r'[^0-9]', '', end_date))
        
        stock_cond = "(sh7code LIKE 'A%') AND" if only_stock else ''
        ohlcv_cond = 'dateint, sh7code, open, high, low, close, vol' if only_ohlcv else '*'
        
        if code == None:
            sql = f"""
            SELECT {ohlcv_cond} FROM {table} 
            WHERE {stock_cond} dateint BETWEEN '{start_date}' AND '{end_date}'
            """
        else:
            sh7code = f"('{code}')" if isinstance(code, str) else tuple(code)
            sql = f"""
            SELECT {ohlcv_cond} FROM {table} 
            WHERE {stock_cond} (sh7code IN {sh7code}) AND (dateint BETWEEN '{start_date}' AND '{end_date}')
            """
        df = pd.read_sql(sql, self.conn)
        return df
    
    def trans_qis_daily_format(self, daily_df, only_ohlcv=False, only_stock=False):
        """Transform DB data format to QIS data format"""
        if ('cddt' in daily_df.columns) or ('open' not in daily_df.columns):
            raise ValueError("You can only input daily data.")

        df = daily_df.copy()
        if only_stock:
            df = df[df['sh7code'].str.contains('A')]

        df['date'] = pd.to_datetime(df['dateint'], format='%Y%m%d')
        df['symbol'] = df['sh7code']

        atf = dict()
        if only_ohlcv:
            atf_keys = df.columns[2:7]
        else:
            atf_keys = df.columns[2:16]

        for key in atf_keys:
            atf[key] = pd.pivot_table(data=df, values=key, index='symbol', columns='date')
            
        return atf
    