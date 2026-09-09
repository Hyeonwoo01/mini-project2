import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def make_session(retries=3, backoff=0.5):
    session = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff,
                  status_forcelist=[429, 500, 502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retry))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session

def fetch_api(session, url, sleep_time=0.1):
    response = session.get(url, timeout=10)
    response.raise_for_status()
    time.sleep(sleep_time) 
    return response.json()