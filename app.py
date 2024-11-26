import redis
import random
import time
from websocket import create_connection, WebSocketException
from utils import json_dmx_parser

ws = create_connection("ws://127.0.0.1:9999/qlcplusWS")

def send_messages(package):
        try:
            for message in package:
                if message['channel'] == 19 or  message['channel'] == 20 or  message['channel'] == 39 or  message['channel'] == 40:
                    continue  
                formated_message = f"CH|{message['channel']}|{message['value']}"
                ws.send(formated_message)
        except WebSocketException as e:
            print(f"WebSocket Handshake: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

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
print(redis_client.get("3:fixyou:so"))

while True:    
    try:
        # data = redis_client.get("3:fixyou:so")
        # if data and data["Status"] != "Stop":
            # get the package using the transformation function
            # Transfom the AI Json data to Pin instructions 
            package = [{"channel": number, "value": int (random.random() * 255)} for number in range(1, 41)]
            send_messages(package=package)
            time.sleep(0.5)

    except KeyboardInterrupt:
            package = [{"channel": number, "value": 0} for number in range(1, 41)]
            send_messages(package=package)
            break