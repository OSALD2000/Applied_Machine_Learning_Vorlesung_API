import random
import time
from websocket import create_connection, WebSocketException
from utils import connect_to_redis, send_messages
import enum
import logging
import time
from schedule import ScheduleManager, STATE
from datetime import datetime, timedelta, timezone

schedule_example ={
            "song_name":"badguy",
            "c": 25,
            "d": 100,
            "st":"Play"
}

ws = create_connection("ws://127.0.0.1:9999/qlcplusWS")
logging.basicConfig(level=logging.INFO)

    
redis_client = connect_to_redis()

schedule_manager = ScheduleManager(redis_client)

while True:    
    try:
        schedule = schedule_example
        schedule_manager.update(schedule=schedule)
        chunk = schedule_manager.get_chunk()
        package = [
             {"channel" : 1, "value": chunk["DMX_1_Pan"]},
             {"channel" : 2, "value": chunk["DMX_2_Tilt"]},
             {"channel" : 3, "value": chunk["DMX_3_Dimmer"]},
             {"channel" : 4, "value": chunk["DMX_4_Strobe"]},
             {"channel" : 5, "value": chunk["DMX_5_Color"]},
             {"channel" : 6, "value": chunk["DMX_6_Gobo"]},
             {"channel" : 7, "value": chunk["DMX_7_Pan_Fine"]},
             {"channel" : 8, "value": chunk["DMX_8_Tilt_Fine"]}
        ]

        send_messages(package=package, ws=ws)
        time.sleep(0.5)
        
    except KeyboardInterrupt:
            package = [{"channel": number, "value": 0} for number in range(1, 41)]
            send_messages(package=package)
            break
    