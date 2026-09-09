import os
import pandas as pd
import pymysql
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

@st.cache_data(ttl=3600)
def get_blueocean_kpi():  
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4'
    )
    query = """
        SELECT 
            m.gu_name, m.dong_name, k.living_pop_2030, k.resident_pop_2030,
            k.activity_ratio, k.cafe_count, k.pop_per_cafe, k.blue_ocean_score, k.region_code
        FROM mart_cafe_blueocean_kpi k
        JOIN dim_region_mapping m ON k.region_code = m.region_code
        ORDER BY k.blue_ocean_score DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=3600)
def get_hourly_pattern(region_code): 
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4'
    )
    query = """
        SELECT time_hour, avg_pop_2030
        FROM mart_hourly_pattern
        WHERE region_code = %s
        ORDER BY time_hour
    """
    df = pd.read_sql(query, conn, params=[region_code])
    conn.close()
    return df