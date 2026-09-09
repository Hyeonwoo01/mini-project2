-- 1. Raw Tables
CREATE TABLE IF NOT EXISTS raw_seoul_living_pop (
    region_code VARCHAR(10),      
    base_date VARCHAR(10),        
    time_hour INT,                
    pop_2030 REAL,                
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_raw_pop ON raw_seoul_living_pop(region_code, base_date);

CREATE TABLE IF NOT EXISTS raw_resident_pop (
    region_code VARCHAR(10) PRIMARY KEY,
    resident_2030 INT,            
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_cafe_stores (
    store_id VARCHAR(50) PRIMARY KEY,
    store_name VARCHAR(255),
    category_mid VARCHAR(100),    
    region_code VARCHAR(10)
);
CREATE INDEX idx_raw_cafe ON raw_cafe_stores(region_code);

-- 2. Dimension Tables
CREATE TABLE IF NOT EXISTS dim_region_mapping (
    region_code VARCHAR(10) PRIMARY KEY,
    gu_name VARCHAR(50),
    dong_name VARCHAR(50)
);

-- 3. Mart Tables
CREATE TABLE IF NOT EXISTS mart_cafe_blueocean_kpi (
    region_code VARCHAR(10) PRIMARY KEY,
    living_pop_2030 REAL,
    resident_pop_2030 REAL,
    activity_ratio REAL,
    cafe_count INT,
    pop_per_cafe REAL,
    blue_ocean_score REAL 
);

CREATE TABLE IF NOT EXISTS mart_hourly_pattern (
    region_code VARCHAR(10),
    time_hour INT,               
    avg_pop_2030 REAL,            
    PRIMARY KEY (region_code, time_hour)
);