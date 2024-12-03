import random
import time
from websocket import create_connection, WebSocketException
from utils import connect_to_redis, send_messages, create_package
import enum
import logging
import time
from schedule import ScheduleManager, STATE
from datetime import datetime, timedelta, timezone

schedule_example = {
            "t": time.time(),
            "song_name":"test",
            "c": 90,
            "d": 100,
            "st":"Play"
}

ws = create_connection("ws://127.0.0.1:9999/qlcplusWS")
logging.basicConfig(level=logging.INFO)

    
redis_client = connect_to_redis()


schedule_manager = ScheduleManager(redis_client)
schedule = schedule_example

while True:    
    try:
        schedule_manager.update(schedule=schedule)
        
        # if schedule_manager.state == STATE.NEW_SONG or  schedule_manager.state == STATE.START_AFTER_PAUSE:
        #     time.sleep()

        if schedule_manager.state != STATE.NO_SONG and schedule_manager.state != STATE.END:
            chunk = schedule_manager.get_chunk()
            package = create_package(chunk)

            msg = f"current Index: {schedule_manager.idx}"
            print(msg)

            send_messages(package=package, ws=ws)
            time.sleep(0.6)
        
        if schedule_manager.state == STATE.END:
            print("END")
            reset_package = [{"channel": number, "value": 0} for number in range(1, 41)]
            send_messages(package=reset_package, ws=ws)
            user_input = int(input("new start "))
            if user_input != 0:
                 schedule = {
                                "t": time.time(),
                                "song_name":"test",
                                "c": user_input,
                                "d": 100,
                                "st":"Play"
                    }
        
    except KeyboardInterrupt:
            package = [{"channel": number, "value": 0} for number in range(1, 41)]
            send_messages(package=package, ws=ws)
            break
    