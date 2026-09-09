-- 1. 지역명 매핑 더미 데이터
INSERT IGNORE INTO dim_region_mapping (region_code, gu_name, dong_name) VALUES 
('99990001', '가상의구', '테스트1동'),
('99990002', '가상의구', '테스트2동'),
('99990003', '가상의구', '테스트3동');

-- 2. 블루오션 KPI 마트 더미 데이터
INSERT IGNORE INTO mart_cafe_blueocean_kpi 
(region_code, living_pop_2030, resident_pop_2030, activity_ratio, cafe_count, pop_per_cafe, blue_ocean_score) 
VALUES 
('99990001', 50000, 5000, 10.0, 5, 10000, 100000),
('99990002', 30000, 15000, 2.0, 10, 3000, 6000),
('99990003', 10000, 10000, 1.0, 20, 500, 500);