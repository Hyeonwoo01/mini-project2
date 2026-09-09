import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def build_data_marts():
    # MariaDB 연결
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    print("1. 블루오션 KPI 마트 테이블 구축")
    
    cursor.execute("DROP TABLE IF EXISTS mart_cafe_blueocean_kpi;")
    cursor.execute("""
        CREATE TABLE mart_cafe_blueocean_kpi (
            region_code VARCHAR(10) PRIMARY KEY,
            living_pop_2030 REAL,
            resident_pop_2030 REAL,
            activity_ratio REAL,
            cafe_count INT,
            pop_per_cafe REAL,
            blue_ocean_score REAL
        );
    """)
    
    kpi_query = """
    INSERT INTO mart_cafe_blueocean_kpi 
        (region_code, living_pop_2030, resident_pop_2030, activity_ratio, cafe_count, pop_per_cafe, blue_ocean_score)
    SELECT 
        r.region_code,
        COALESCE(l.total_living_pop, 0) AS living_pop_2030,
        r.resident_2030 AS resident_pop_2030,
        
        -- 활동 배율: 생활인구 / 거주인구
        CASE WHEN r.resident_2030 > 0 THEN COALESCE(l.total_living_pop, 0) / r.resident_2030 ELSE 0 END AS activity_ratio,
        
        COALESCE(c.cafe_count, 0) AS cafe_count,
        
        -- 카페당 인구: 생활인구 / 카페 수 (카페가 0이면 생활인구 전체)
        CASE WHEN COALESCE(c.cafe_count, 0) > 0 THEN COALESCE(l.total_living_pop, 0) / c.cafe_count ELSE COALESCE(l.total_living_pop, 0) END AS pop_per_cafe,
        
        -- 블루오션 지수: 활동 배율 * 카페당 인구
        (CASE WHEN r.resident_2030 > 0 THEN COALESCE(l.total_living_pop, 0) / r.resident_2030 ELSE 0 END) * 
        (CASE WHEN COALESCE(c.cafe_count, 0) > 0 THEN COALESCE(l.total_living_pop, 0) / c.cafe_count ELSE COALESCE(l.total_living_pop, 0) END) AS blue_ocean_score
        
    FROM raw_resident_pop r
    LEFT JOIN (
        SELECT region_code, SUM(pop_2030) as total_living_pop
        FROM raw_seoul_living_pop
        GROUP BY region_code
    ) l ON r.region_code = l.region_code
    LEFT JOIN (
        SELECT region_code, COUNT(store_id) as cafe_count
        FROM raw_cafe_stores
        GROUP BY region_code
    ) c ON r.region_code = c.region_code;
    """
    cursor.execute(kpi_query)

    print("2. 시간대별 패턴 마트 테이블 구축")
    
    cursor.execute("DROP TABLE IF EXISTS mart_hourly_pattern;")
    cursor.execute("""
        CREATE TABLE mart_hourly_pattern (
            region_code VARCHAR(10),
            time_hour INT,
            avg_pop_2030 REAL,
            PRIMARY KEY (region_code, time_hour)
        );
    """)
    
    # 시간대별 평균 생활인구 계산
    hourly_query = """
    INSERT INTO mart_hourly_pattern (region_code, time_hour, avg_pop_2030)
    SELECT region_code, time_hour, AVG(pop_2030)
    FROM raw_seoul_living_pop
    GROUP BY region_code, time_hour;
    """
    cursor.execute(hourly_query)

    conn.commit()
    conn.close()
    print("데이터 마트 구축 및 블루오션 지수 산출이 완료")

if __name__ == "__main__":
    build_data_marts()