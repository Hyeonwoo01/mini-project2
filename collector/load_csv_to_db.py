import os
import pandas as pd
import pymysql
from dotenv import load_dotenv

load_dotenv()

def load_csv_data():
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    print("1. 거주인구 데이터 적재")
    df_pop = pd.read_csv("miniproject2/data/raw/resident_pop.csv", encoding="utf-8")
    
    target_cols = [f"{i}세남자" for i in range(20, 40)] + [f"{i}세여자" for i in range(20, 40)]
    
    df_pop['resident_2030'] = df_pop[target_cols].sum(axis=1)
    
    df_pop['region_code'] = df_pop['행정기관코드'].astype(str).str.replace('.0', '', regex=False).str[:8]
    
    pop_data = df_pop[['region_code', 'resident_2030']].values.tolist()
    
    cursor.execute("TRUNCATE TABLE raw_resident_pop")
    cursor.executemany(
        "INSERT INTO raw_resident_pop (region_code, resident_2030) VALUES (%s, %s)",
        pop_data
    )
    print(f" -> 거주인구 {len(pop_data)}건 적재")

    print("2. 카페 상가 데이터 적재")
    df_cafe = pd.read_csv("miniproject2/data/raw/cafe_data.csv", encoding="utf-8", low_memory=False)
    
    df_cafe = df_cafe[df_cafe['상권업종소분류명'].str.contains('카페|커피|빵/도넛', na=False, regex=True)]
    
    df_cafe['region_code'] = df_cafe['행정동코드'].astype(str).str.replace('.0', '', regex=False).str[:8]
    df_cafe['상호명'] = df_cafe['상호명'].fillna('이름없음')
    
    cafe_data = df_cafe[['상가업소번호', '상호명', '상권업종소분류명', 'region_code']].values.tolist()
    
    cursor.execute("TRUNCATE TABLE raw_cafe_stores")
    cursor.executemany(
        "INSERT INTO raw_cafe_stores (store_id, store_name, category_mid, region_code) VALUES (%s, %s, %s, %s)",
        cafe_data
    )
    print(f" -> 경쟁 카페 점포 {len(cafe_data)}건 적재")

    conn.commit()
    conn.close()
    print("모든 기초 데이터 DB 적재 완료")

if __name__ == "__main__":
    load_csv_data()