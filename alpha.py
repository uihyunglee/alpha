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
    
    
    def __del__(self):
        self.conn.close()
        
        
    def get_table_names(self):
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
        table_name = pd.read_sql(sql, self.conn)
        return list(table_name.values.reshape(-1))
    
    
    def get_stock_data(self, table, code=None, start_date=None, end_date=None):
        if start_date == None:
            start_date = '0'
        if end_date == None:
            end_date = '3000_00_00'
        
        start_date = int(re.sub(r'[^0-9]', '', start_date))
        end_date = int(re.sub(r'[^0-9]', '', end_date))
        
        if code == None:
            sql = f"SELECT * FROM {table} WHERE dateint>='{start_date}' AND dateint<='{end_date}';"
        else:
            sql = f"SELECT * FROM {table} WHERE sh7code='{code}' AND dateint>='{start_date}' AND dateint<='{end_date}';"
        
        df = pd.read_sql(sql, self.conn)
        
        return df