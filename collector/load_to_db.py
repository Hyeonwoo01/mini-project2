import os
import json
import pymysql
import logging
from dotenv import load_dotenv

load_dotenv()

log_dir = "data/logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=f"{log_dir}/db_load.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def load_json_to_db(filepath):
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    with open(filepath, 'r', encoding='utf-8') as f:
        rows = json.load(f)

    insert_query = """
        INSERT INTO raw_seoul_living_pop (region_code, base_date, time_hour, pop_2030)
        VALUES (%s, %s, %s, %s)
    """

    data_to_insert = []
    
    for row in rows:
        region_code = row.get('ADSTRD_CODE_SE')
        raw_date = row.get('STDR_DE_ID') 
        base_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
        time_hour = int(row.get('TMZON_PD_SE'))

        pop_2030 = (
            float(row.get('MALE_F20T24_LVPOP_CO', 0)) +
            float(row.get('MALE_F25T29_LVPOP_CO', 0)) +
            float(row.get('MALE_F30T34_LVPOP_CO', 0)) +
            float(row.get('MALE_F35T39_LVPOP_CO', 0)) +
            float(row.get('FEMALE_F20T24_LVPOP_CO', 0)) +
            float(row.get('FEMALE_F25T29_LVPOP_CO', 0)) +
            float(row.get('FEMALE_F30T34_LVPOP_CO', 0)) +
            float(row.get('FEMALE_F35T39_LVPOP_CO', 0))
        )

        data_to_insert.append((region_code, base_date, time_hour, pop_2030))

    cursor.executemany(insert_query, data_to_insert)
    conn.commit()
    conn.close()

    success_msg = f"[{str(time_hour).zfill(2)}시] {len(data_to_insert)}건 적재 완료"
    print(success_msg)
    logging.info(success_msg)

if __name__ == "__main__":
    logging.info("DB 적재 작업 시작")
    
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE raw_seoul_living_pop")
    conn.commit()
    conn.close()

    for hour in range(24):
        target_time = str(hour).zfill(2)
        file_path = f"data/raw/living_pop_20260715_{target_time}.json"
        
        if os.path.exists(file_path):
            load_json_to_db(file_path)
        else:
            fallback_path = f"../data/raw/living_pop_20260715_{target_time}.json"
            if os.path.exists(fallback_path):
                load_json_to_db(fallback_path)
            else:
                error_msg = f"파일을 찾을 수 없습니다: {file_path}"
                print(error_msg)
                logging.error(error_msg)
                
    logging.info("DB 적재 작업 완료")