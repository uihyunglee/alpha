from typing import Dict, List
from datetime import datetime as dt

import pandas as pd
import psycopg2
import json
import re
import os


class AlphaDB:
    def __init__(self, conn_info: str | dict, info_key: str = ''):
        """
        This class connects to remote DB with conn_info, creates connection, and prepares to fetch data.

        Parameters
        ----------
        conn_info: filepath-str | dict
            filepath-str must be existing file path (ends with .json or .yaml)
            dict or loaded-dict from file must contain connection info with key and value as below.
             1) PostgreSQL: host, port, user, password, dbname

        info_key: (optional) str, default ''
            If specified, use this key to load connection info in conn_info[info_key]  (read subtree, not root)
        """

        conn_kwargs = {}
        if isinstance(conn_info, str):
            if os.path.isfile(conn_info):
                if conn_info.endswith('.json'):
                    with open(conn_info, "r") as info:
                        _info = json.load(info)
                        conn_kwargs.update(_info[info_key] if info_key else _info)
                elif conn_info.endswith('.yaml') or conn_info.endswith('.yml'):
                    _info = {}  # todo: support yaml loading
                    conn_kwargs.update(_info[info_key] if info_key else _info)
                else:
                    raise ValueError(f"not supported file type: {conn_info.split('.')[-1]}")
            else:
                raise FileNotFoundError(f"conn_info file not found: {conn_info}")
        elif isinstance(conn_info, dict):
            conn_kwargs = conn_info
        else:
            raise ValueError(f"conn_info must be existing file path str (.json or .yaml) or dict. not {type(conn_info)}")

        self.conn = psycopg2.connect(**conn_kwargs)

    def get_table_names(self) -> List[str]:
        """Return DB table name"""
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        table_name = pd.read_sql(sql, self.conn)
        return list(table_name.values.reshape(-1))

    def get_stock_data(self, table_name: str, code: str | List[str] = 'all', 
                   start_date: str = '2023_01_01', end_date: str = '3000_00_00',
                   except_etn: bool = False, only_ohlcv: bool = False) -> pd.DataFrame:
        """Return stock data in table"""
        start_date = start_date.strftime('%Y%m%d') if isinstance(start_date, dt) else start_date
        end_date = end_date.strftime('%Y%m%d') if isinstance(end_date, dt) else end_date
        start_date = int(re.sub(r'[^0-9]', '', start_date))
        end_date = int(re.sub(r'[^0-9]', '', end_date))

        code = code if isinstance(code, str) else str(code)[2:-2]

        cond_code = f"AND sh7code IN ('{code}')" if code != 'all' else ''
        cond_not_etn = "AND (sh7code NOT LIKE 'Q%')" if except_etn else ''
        cond_only_ohlcv = 'dateint, sh7code, open, high, low, close, vol' if only_ohlcv else '*'
        cond_only_ohlcv = cond_only_ohlcv if table_name.split('_')[-1] == 'daily' else 'cddt,' + cond_only_ohlcv

        sql = f"""
        SELECT {cond_only_ohlcv} FROM {table_name} 
        WHERE dateint BETWEEN '{start_date}' AND '{end_date}'
        {cond_not_etn}
        {cond_code}
        ;
        """
        df = pd.read_sql(sql, self.conn)
        return df
    
    def get_date_Ndays_ago(self, today: str, N: int) -> str:
        """Return date Ndays ago"""
        today = today.strftime('%Y%m%d') if isinstance(today, dt) else today
        today = int(re.sub(r'[^0-9]', '', today))
        with self.conn.cursor() as curs:
            sql = f"""
            SELECT DISTINCT dateint FROM cpstore_adjchart_daily
            WHERE dateint < {today}
            ORDER BY dateint DESC
            LIMIT 1 OFFSET {N-1}
            """
            curs.execute(sql)
            res = curs.fetchone()
            date = str(res[0])
            return f'{date[:4]}-{date[4:6]}-{date[6:]}'
    
    def get_krx_closed_bday(self) -> List[str]:
        """Return KRX closed days except weekends"""
        with self.conn.cursor() as curs:
            sql = f"""
            SELECT json_data FROM common_jsonstore
            WHERE key = 'krx_closed_bday_li'
            ;
            """
            curs.execute(sql)
            res = curs.fetchone()
        return res[0]

    @staticmethod
    def trans_qis_daily_format(daily_df: pd.DataFrame, only_ohlcv: bool = False, filter_out_etn: bool = False,
                               transposed: bool = True) -> Dict[str, pd.DataFrame]:
        """Transform DB data format to QIS data format"""
        if ('cddt' in daily_df.columns) or ('open' not in daily_df.columns):
            raise ValueError("You can only input daily data.")

        df = daily_df.copy()
        if filter_out_etn:
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
            if transposed:
                atf[key] = atf[key].T

        return atf