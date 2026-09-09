
-- 시간대별 유동인구 패턴 마트 테이블 갱신
TRUNCATE TABLE mart_hourly_pattern;

INSERT INTO mart_hourly_pattern (region_code, time_hour, avg_pop_2030)
SELECT 
    region_code,
    time_hour,
    AVG(pop_2030) AS avg_pop_2030
FROM raw_seoul_living_pop
GROUP BY region_code, time_hour;

-- 상권 분석 블루오션 KPI 마트 테이블 갱신
TRUNCATE TABLE mart_cafe_blueocean_kpi;

INSERT INTO mart_cafe_blueocean_kpi (
    region_code, 
    living_pop_2030, 
    resident_pop_2030, 
    activity_ratio, 
    cafe_count, 
    pop_per_cafe, 
    blue_ocean_score
)
WITH daily_living AS (
    -- 일자별/행정동별 유동인구 총합 계산
    SELECT 
        region_code, 
        base_date, 
        SUM(pop_2030) AS total_pop
    FROM raw_seoul_living_pop
    GROUP BY region_code, base_date
),
avg_living AS (
    -- 행정동별 일평균 유동인구 계산
    SELECT 
        region_code, 
        AVG(total_pop) AS living_pop_2030
    FROM daily_living
    GROUP BY region_code
),
cafe_cnt AS (
    -- 행정동별 경쟁 카페 수 계산
    SELECT 
        region_code, 
        COUNT(store_id) AS cafe_count
    FROM raw_cafe_stores
    GROUP BY region_code
)
-- 종 KPI 지표 연산 및 적재
SELECT 
    r.region_code,
    COALESCE(l.living_pop_2030, 0) AS living_pop_2030,
    COALESCE(p.resident_2030, 0) AS resident_pop_2030,
    
    -- 주간 활동 배율 = 유동인구 / 거주인구 (분모가 0일 경우 에러 방지)
    COALESCE(l.living_pop_2030 / NULLIF(p.resident_2030, 0), 0) AS activity_ratio,
    
    COALESCE(c.cafe_count, 0) AS cafe_count,
    
    -- 점포당 잠재고객 = 유동인구 / 카페 수
    COALESCE(l.living_pop_2030 / NULLIF(c.cafe_count, 0), 0) AS pop_per_cafe,
    
    -- 블루오션 지수 = 활동 배율 × 점포당 잠재고객
    COALESCE(
        (l.living_pop_2030 / NULLIF(p.resident_2030, 0)) * 
        (l.living_pop_2030 / NULLIF(c.cafe_count, 0)), 
    0) AS blue_ocean_score

FROM dim_region_mapping r
LEFT JOIN avg_living l ON r.region_code = l.region_code
LEFT JOIN raw_resident_pop p ON r.region_code = p.region_code
LEFT JOIN cafe_cnt c ON r.region_code = c.region_code;