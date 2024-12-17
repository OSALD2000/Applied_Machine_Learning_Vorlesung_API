import time
import logging
import json
from datetime import datetime
from websocket import create_connection, WebSocketException
from utils import connect_to_redis, send_messages_moving_heads, create_package, send_messages_leds
from schedule import ScheduleManager, STATE
from datetime import datetime, timezone


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FIRST_SEND = True

try:
    ws_1 = create_connection("ws://127.0.0.1:9999/qlcplusWS")
    ws_2 = create_connection("ws://192.168.171.27/ws")
    pattern = {
            "bri": 255,
            "seg": {
                "pal":4,
                "fx": 128,
            },
            "v": True,
            "time": time.time()
        }
   
    ws_2.send(json.dumps(pattern))

    logging.info("Connected to WebSocket.")
except WebSocketException as e:
    logging.error(f"WebSocket connection failed: {e}")
    exit(1)

redis_client = connect_to_redis()

schedule_manager = ScheduleManager(redis_client)

def create_reset_package():
    package =  [{"channel": number, "value": 0 } for number in range(1, 41)]
    
    package[0]['value'] = 150
    package[2]['value'] = 40
    package[20]['value'] = 190
    package[22]['value'] = 40
    
    return package

def create_rest_package_leds():
       return {
            "seg": {
                "ix": 255,
                "sx": min(led_package[0]["value"] + 40, 255),
                "col": [
                [
                    255,
                    255,
                    255,
                    0
                ],
                    [
                    255,
                    255,
                    255,
                    0
                ],  [
                    255,
                    255,
                    255,
                    0
                ]
                ]
            },
            "v": True,
            "time": time.time()
        }
   
obj = redis_client.get("3:sc")
if obj:
    schedule = json.loads(obj)
else:
    schedule = None

try:
    while True:
        schedule_manager.update(schedule=schedule)
        if schedule_manager.state in {STATE.NEW_SONG, STATE.START_AFTER_PAUSE}:
            timestamp = datetime.strptime(schedule_manager.current_schedule['t'], "%Y-%m-%d %H:%M:%S")
            print("timestamp:",timestamp.timestamp())
            milliseconds = int(timestamp.timestamp())
            print("millis ", milliseconds)
            sleep_time = time.time() - milliseconds
            print("sleep ", time.time())
            if sleep_time < 0:
                time.sleep(abs(sleep_time))

        if schedule_manager.state not in {STATE.NO_SONG, STATE.END}:
            chunk = schedule_manager.get_chunk()
            package, led_package = create_package(chunk)
            logging.info(f"Current Index: {schedule_manager.idx}")
            send_messages_moving_heads(package=package, ws=ws_1)
            if schedule_manager.idx % 14 == 0 or FIRST_SEND:
                send_messages_leds(package=package, led_package=led_package, ws=ws_2)
                FIRST_SEND = False

            time.sleep(0.45)

        if schedule_manager.state == STATE.END:
            logging.info("Song ended. Resetting channels.")
            send_messages_moving_heads(package=create_reset_package(), ws=ws_1)
            send_messages_leds(package=create_rest_package_leds(), led_package=led_package, ws=ws_2)

        obj = redis_client.get("3:sc")
        if obj:
            schedule = json.loads(obj)
        else:
            schedule = None

except KeyboardInterrupt:
    logging.info("Keyboard interrupt detected. Resetting channels and exiting.")
    send_messages_moving_heads(package=create_reset_package(), ws=ws_1)

except Exception as e:
    logging.error(f"Unexpected error: {e}")

finally:
    if ws_1:
        ws_1.close()
    if ws_2:
        ws_2.close()    

    logging.info("WebSocket connection closed.")
