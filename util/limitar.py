import json
import os

import redis
import time

import logging

TIME_WINDOW = float(os.getenv('TIME_WINDOW'))
REQUEST_LIMIT = int(os.getenv('REQUEST_LIMIT'))

logger = logging.getLogger("utils")

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)

logger.addHandler(c_handler)

def get_redis_connection():
    host = os.getenv('REDIS_HOST')
    port = os.getenv('REDIS_PORT')
    passwd = os.getenv('REDIS_PASS')
    r = redis.Redis(host=host, port=port, password=passwd, db=0)

    return r


def limit_request(remote_address):
    conn = get_redis_connection()
    record = conn.get(remote_address)

    current = time.time()
    if record is None:
        set_data = {
            "ts": current,
            "count": 1
        }
        conn.set(remote_address, json.dumps(set_data))

        return False

    data = json.loads(record)
    queue_len = data.get('count')
    if queue_len <= REQUEST_LIMIT:
        data['count'] = queue_len + 1
        conn.set(remote_address, json.dumps(data))

        return False

    delta = current - data.get('ts')
    if delta <= TIME_WINDOW:
        return True

    set_data = {
        "ts": current,
        "count": 1
    }
    conn.set(remote_address, json.dumps(set_data))

    return False
