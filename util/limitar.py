import json
import os

import redis
import time

TIME_WINDOW = os.getenv('TIME_WINDOW')
REQUEST_LIMIT = os.getenv('REQUEST_LIMIT')


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
            "ts_queue": [current]
        }
        conn.set(remote_address, json.dumps(set_data))

        return False

    data = json.loads(record)
    ts_queue = data.get('ts_queue', [])
    queue_len = len(ts_queue)

    if queue_len < REQUEST_LIMIT:
        return False

    sorted_ts = sorted(ts_queue)
    earliest = sorted_ts[0]
    delta = current - earliest

    if delta < TIME_WINDOW:
        return True

    ts_queue.pop()
    ts_queue.append(current)
    set_data = {
        "ts_queue": ts_queue
    }

    conn.set(remote_address, json.dumps(set_data))

    return False
