import os
import logging
from dotenv import load_dotenv

from collector.seoul_pop import collect_living_pop
from collector.load_to_db import load_json_to_db
import pymysql

load_dotenv()

log_dir = "miniproject2/data/logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=f"{log_dir}/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def run_pipeline():
    target_date = "20260715"
    print("생활인구 24시간 데이터 수집 시작")
    
    # 데이터 수집
    for hour in range(24):
        target_time = str(hour).zfill(2)
        collect_living_pop(target_date, target_time)
        
    print("데이터 수집 완료. DB 적재 시작")
    
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME'), charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE raw_seoul_living_pop")
    conn.commit()
    conn.close()

    # 데이터 적재
    for hour in range(24):
        target_time = str(hour).zfill(2)
        file_path = f"miniproject2/data/raw/living_pop_{target_date}_{target_time}.json"
        
        if os.path.exists(file_path):
            load_json_to_db(file_path)
        else:
            fallback_path = f"../data/raw/living_pop_{target_date}_{target_time}.json"
            if os.path.exists(fallback_path):
                load_json_to_db(fallback_path)
                
    print("파이프라인 전체 실행 완료")
    logging.info("전체 수집 및 적재 파이프라인 정상 종료")

if __name__ == "__main__":
    run_pipeline()