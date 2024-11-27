import random
import time
from websocket import create_connection, WebSocketException
from utils import json_dmx_parser, connect_to_redis, send_messages, load_song, calculate_start_point
import enum
import logging
import time
from schedule import Schedule, STATE
from datetime import datetime, timedelta, timezone


logging.basicConfig(level=logging.INFO)

    
redis_client = connect_to_redis()


CURRENT_SCHEDULE_STATE = STATE.NO_SONG
OLD_SCHEDULE_STATE = STATE.NO_SONG


while True:    
    try:
        schedule = redis_client.get("2:HeavyIsTheCrown:so")
        
        song = redis_client.get("2:using the song name")

        if schedule and schedule["st"] != "Stop":
            # get the package using the transformation function
            # Transfom the AI Json data to Pin instructions 
            package = [{"channel": number, "value": int (random.random() * 255)} for number in range(1, 41)]
            send_messages(package=package, ws=ws)
            time.sleep(0.5)

    except KeyboardInterrupt:
            package = [{"channel": number, "value": 0} for number in range(1, 41)]
            send_messages(package=package)
            break
    