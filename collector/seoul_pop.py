import os
import json
import logging
from dotenv import load_dotenv
from collector.client import make_session, fetch_api

load_dotenv()
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")

log_dir = "data/logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=f"{log_dir}/api_collection.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def collect_living_pop(target_date, target_time):
    session = make_session()
    
    start_idx = 1
    end_idx = 1000
    service_name = "SPOP_LOCAL_RESD_DONG"
    
    url = f"http://openapi.seoul.go.kr:8088/{SEOUL_API_KEY}/json/{service_name}/{start_idx}/{end_idx}/{target_date}/{target_time}"
    
    try:
        msg_start = f"[{target_date} {target_time}시] 데이터 수집 요청 중"
        print(msg_start)
        logging.info(msg_start)
        
        data = fetch_api(session, url)
        
        if service_name in data:
            row_count = data[service_name]['list_total_count']
            rows = data[service_name]['row']
            
            msg_count = f"총 {row_count}건의 데이터를 가져왔습니다."
            print(msg_count)
            logging.info(msg_count)
            
            save_dir = "data/raw"
            os.makedirs(save_dir, exist_ok=True)
            
            file_name = f"{save_dir}/living_pop_{target_date}_{target_time}.json"
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=2)
                
            msg_save = f"데이터 저장 완료: {file_name}"
            print(msg_save)
            logging.info(msg_save)
            
            return rows
        else:
            msg_err = f"API 응답 에러: {data}"
            print(msg_err)
            logging.error(msg_err)
            return None
            
    except Exception as e:
        msg_fatal = f"수집 중 치명적 오류 발생: {e}"
        print(msg_fatal)
        logging.error(msg_fatal)
        return None

if __name__ == "__main__":
    target_date = "20260715"
    msg_init = f"{target_date} 생활인구 24시간 수집 시작"
    print(msg_init)
    logging.info(msg_init)

    for hour in range(24):
        target_time = str(hour).zfill(2)
        collect_living_pop(target_date, target_time)
        
    msg_done = "24시간 데이터 수집 완료"
    print(msg_done)
    logging.info(msg_done)