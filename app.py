import redis
import json
from movingHead import MovingHead
from utils import json_dmx_parser

def connect_to_redis():
    try:
        redis_client = redis.Redis(
            host= '130.61.189.22',
            port=6379,      
            db=0       
        )
        
        redis_client.ping()
        print("Connected to Redis!")
        return redis_client
    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
        return None

redis_client = connect_to_redis()
movinghead = MovingHead()

# read from redis
# move the Moving head