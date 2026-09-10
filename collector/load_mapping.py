import os
import pandas as pd
import pymysql
from dotenv import load_dotenv

load_dotenv()

def build_region_mapping():
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    print("행정동 매핑 테이블 구축")
    
    cursor.execute("DROP TABLE IF EXISTS dim_region_mapping;")
    cursor.execute("""
        CREATE TABLE dim_region_mapping (
            region_code VARCHAR(10) PRIMARY KEY,
            gu_name VARCHAR(50),
            dong_name VARCHAR(50)
        );
    """)

    df_pop = pd.read_csv("data/raw/resident_pop.csv", encoding="utf-8")
    
    df_pop['region_code'] = df_pop['행정기관코드'].astype(str).str.replace('.0', '', regex=False).str[:8]
    
    df_mapping = df_pop[['region_code', '시군구명', '읍면동명']].dropna().drop_duplicates(subset=['region_code'])
    mapping_data = df_mapping.values.tolist()

    cursor.executemany(
        "INSERT INTO dim_region_mapping (region_code, gu_name, dong_name) VALUES (%s, %s, %s)",
        mapping_data
    )
    
    conn.commit()
    conn.close()
    print(f"총 {len(mapping_data)}개의 지역명 매핑 데이터가 DB에 적재")

if __name__ == "__main__":
    build_region_mapping()